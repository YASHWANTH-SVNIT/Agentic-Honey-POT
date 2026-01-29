from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import MessageRequest, MessageResponse
from app.api.dependencies import get_api_key
from app.services.session.manager import get_session_manager
from app.services.detection.pipeline import get_detection_pipeline

router = APIRouter()

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
    
    # 3. Route Decision: Detection vs Engagement
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
            
            return MessageResponse(
                reply=reply_text,
                action="engage",
                metadata={
                    "scam_detected": True,
                    "category": session.category,
                    "stage": session.stage,
                    "turn": session.turn_count,
                    "persona": getattr(session, 'persona', None),
                    "extracted_intel": session.extracted_intel
                }
            )
            
        # Normal detection response (Probe or Ignore)
        reply = None
        if action == "probe":
            reply = "I see. Can you provide more details so I can assist better?"
            
        return MessageResponse(
            reply=reply,
            action=action,
            metadata={
                "status": "monitored",
                "category": getattr(decision, "category", None) if decision else None
            }
        )
    
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
        
        return MessageResponse(
            reply=reply_text,
            action="engage",
            metadata={
                "scam_detected": True,
                "category": session.category,
                "stage": session.stage,
                "turn": session.turn_count,
                "persona": getattr(session, 'persona', None),
                "extracted_intel": session.extracted_intel
            }
        )
