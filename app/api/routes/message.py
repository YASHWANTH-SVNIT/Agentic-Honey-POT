from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import MessageRequest, MessageResponse, EngagementMetrics, ExtractedIntelligence
from app.api.dependencies import get_api_key
from app.services.session.manager import get_session_manager
from app.services.detection.pipeline import get_detection_pipeline
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter()
import settings

def map_intel_to_schema(session_intel: Dict[str, Any], red_flags: List[str]) -> ExtractedIntelligence:
    """
    Maps AI-extracted intelligence to GUVI schema format.
    """
    return ExtractedIntelligence(
        # Direct mappings
        upiIds=session_intel.get("upiIds", []),
        phoneNumbers=session_intel.get("phoneNumbers", []),
        bankAccounts=session_intel.get("bankAccounts", []),
        phishingLinks=session_intel.get("phishingLinks", []),

        # Extended fields
        amounts=session_intel.get("amounts", []),
        bankNames=session_intel.get("bankNames", []),
        ifscCodes=session_intel.get("ifscCodes", []),
        emailAddresses=session_intel.get("emailAddresses", []),

        # New fields (Change 5)
        caseIds=session_intel.get("caseIds", []),
        policyNumbers=session_intel.get("policyNumbers", []),
        orderNumbers=session_intel.get("orderNumbers", []),

        # Combine red flags with any extracted keywords
        suspiciousKeywords=red_flags + session_intel.get("keywords", [])
    )

@router.post("/message", response_model=MessageResponse)
async def handle_message(
    request: MessageRequest,
    api_key: str = Depends(get_api_key)
):
    # 1. Initialize services
    session_manager = get_session_manager()
    pipeline = get_detection_pipeline()
    
    # 2. Load or create session
    session = session_manager.get_session(request.sessionId)
    if not session:
        session = session_manager.create_session(request.sessionId)
        # Robustness: Recover state if history exists (e.g., server restart)
        if request.conversationHistory:
            session.turn_count = len(request.conversationHistory) // 2
            session.scam_detected = True  # History means scam was already detected - skip re-detection
            print(f"[API] Restored session: Turn {session.turn_count}, scam_detected=True (skipping detection)")
    
    # Check for Phase 9: Session Closure
    if getattr(session, "reported_to_guvi", False):
        print(f"[API] Session {request.sessionId} already reported/closed.")
        duration = int((datetime.now() - session.created_at).total_seconds())
        msg_count = session.turn_count * 2
        
        return MessageResponse(
            status="success",
            scamDetected=True,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=duration,
                totalMessagesExchanged=msg_count
            ),
            extractedIntelligence=map_intel_to_schema(session.extracted_intel, session.red_flags),
            agentNotes="Session closed.",
            reply=None,
            action="session_ended"
        )

    # 3. Route Decision: Detection vs Engagement
    reply_text = None
    
    if not session.scam_detected:
        # PHASE 2: Detection Pipeline
        print(f"[API] Processing for detection: {request.sessionId}")
        result = await pipeline.process(request)
        
        action = result.get("action", "ignore")
        decision = result.get("decision")
        
        # Refresh session to check for state changes
        session = session_manager.get_session(request.sessionId)
        
        if session.scam_detected:
            # Seamless transition: Generate first engagement response immediately
            print(f"[API] Seamless transition to Engagement: {request.sessionId}")
            
            from app.services.engagement.agent import EngagementAgent
            
            # Generate response using the selected persona
            reply_text = await EngagementAgent.generate_response(
                session=session,
                message_text=request.message.text,
                history=request.conversationHistory
            )
            
            # Update session
            session_manager.update_session(session)
            
        else:
            # Check for language not supported
            if action == "not_supported":
                return MessageResponse(
                    status="error",
                    scamDetected=False,
                    engagementMetrics=EngagementMetrics(
                        engagementDurationSeconds=0,
                        totalMessagesExchanged=0
                    ),
                    extractedIntelligence=ExtractedIntelligence(),
                    agentNotes=result.get("reason", "Language not supported"),
                    reply=None,
                    action="not_supported"
                )
            # Normal detection response (Probe or Ignore)
            elif action == "probe":
                reply_text = "I see. Can you provide more details so I can assist better?"
            else:
                # IGNORE action - no reply
                reply_text = None
    
    # 4. PHASE 3: Engagement Pipeline
    else:
        print(f"[API] Routing to Engagement: {request.sessionId}")
        
        from app.services.engagement.agent import EngagementAgent
        
        message_text = request.message.text
        reply_text = await EngagementAgent.generate_response(
            session=session,
            message_text=message_text,
            history=request.conversationHistory
        )
        
        # Update session
        session_manager.update_session(session)

    # 5. Construct Final Response Payload (GUVI Hackathon Format)
    
    # Calculate Metrics
    duration = int((datetime.now() - session.created_at).total_seconds())
    msg_count = session.turn_count * 2
    
    # Construct Agent Notes — use LLM-generated red flags from detection phase
    red_flags = getattr(session, 'red_flags', []) or []
    extracted_intel = getattr(session, 'extracted_intel', {}) or {}

    # Deduplicate, preserve order
    unique_flags = list(dict.fromkeys(red_flags))

    if unique_flags:
        notes = (
            f"Scam type: {session.category or 'unknown'}. "
            f"Stage: {session.stage}. "
            f"Red flags: {'; '.join(unique_flags[:8])}."
        )
    else:
        notes = (
            f"Scam type: {session.category or 'unknown'}. "
            f"Stage: {session.stage}. "
            f"Reasoning: {getattr(session, 'reasoning', '')[:100]}."
        )



    response = MessageResponse(
        sessionId=request.sessionId,
        status="success",
        scamDetected=session.scam_detected,
        totalMessagesExchanged=msg_count,
        engagementDurationSeconds=duration,
        engagementMetrics=EngagementMetrics(
            engagementDurationSeconds=duration,
            totalMessagesExchanged=msg_count
        ),
        extractedIntelligence=map_intel_to_schema(extracted_intel, red_flags),
        agentNotes=notes,
        scamType=session.category,
        confidenceLevel=float(session.confidence) if session.confidence else None,
        reply=reply_text,
        action="engage" if session.scam_detected else "ignore"
    )

    return response