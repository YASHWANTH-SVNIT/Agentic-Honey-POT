from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import MessageRequest, MessageResponse
from app.api.dependencies import get_api_key
from app.services.session.manager import SessionManager

router = APIRouter()

@router.post("/message", response_model=MessageResponse)
async def handle_message(
    request: MessageRequest,
    api_key: str = Depends(get_api_key)
):
    # 1. Load or create session
    session = SessionManager.get_or_create_session(request.sessionId)
    
    # 2. Extract context
    message_text = request.message.text
    
    # 3. Route Decision (Phase 1 Logic)
    if not session.scam_detected:
        # ROUTE: Detection Pipeline (Phase 2 - To be implemented)
        # For now: Just a placeholder that would trigger detection
        print(f"Routing to Detection Pipeline: {message_text}")
        
        # This is where we would call app.services.detection.pipeline.process()
        return MessageResponse(
            reply="Processing your message...", # Placeholder
            action="ignore", # Default action if detection isn't ready
            metadata={"status": "detection_pending"}
        )
    else:
        # ROUTE: Engagement Pipeline (Phase 3 - To be implemented)
        print(f"Routing to Engagement Pipeline: {message_text}")
        
        # This is where we would call app.services.engagement.agent.generate_response()
        return MessageResponse(
            reply="I'm not sure what to do yet.", # Placeholder
            action="continue",
            metadata={"status": "engagement_pending"}
        )
