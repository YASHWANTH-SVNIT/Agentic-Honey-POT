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
        
        # Simple response generation based on detection
        reply = None
        if action == "engage":
            reply = "I understand. This sounds very serious. How can I help?"
        elif action == "probe":
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
