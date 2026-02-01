from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import MessageRequest, MessageResponse, EngagementMetrics, ExtractedIntelligence
from app.api.dependencies import get_api_key
from app.services.session.manager import get_session_manager
from app.services.detection.pipeline import get_detection_pipeline
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter()

def map_intel_to_schema(session_intel: Dict[str, Any], red_flags: List[str]) -> ExtractedIntelligence:
    return ExtractedIntelligence(
        bankAccounts=session_intel.get("bank_account", []),
        upiIds=session_intel.get("upi_id", []),
        phishingLinks=session_intel.get("url", []),
        phoneNumbers=session_intel.get("phone_number", []),
        suspiciousKeywords=red_flags + session_intel.get("keywords", []) # Combine red flags and extracted keywords
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
    
    # Check for Phase 9: Session Closure
    # If session is already closed/reported, stop replying
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
        
        # Refresh session to check for state changes (e.g., transition to engagement)
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
            # Normal detection response (Probe or Ignore)
            if action == "probe":
                reply_text = "I see. Can you provide more details so I can assist better?"
    
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
    msg_count = session.turn_count * 2 # Approximation for total messages
    
    # Construct Agent Notes
    notes = f"Category: {session.category}. Stage: {session.stage}. "
    if session.reasoning:
        notes += f"Reasoning: {session.reasoning[:50]}..."
        
    response = MessageResponse(
        status="success",
        scamDetected=session.scam_detected,
        engagementMetrics=EngagementMetrics(
            engagementDurationSeconds=duration,
            totalMessagesExchanged=msg_count
        ),
        extractedIntelligence=map_intel_to_schema(session.extracted_intel, session.red_flags),
        agentNotes=notes,
        reply=reply_text,
        action="engage" if session.scam_detected else "ignore"
    )
    
    return response
