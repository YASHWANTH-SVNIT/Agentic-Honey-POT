from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    sender: str
    text: str
    timestamp: Optional[str] = None

class MessageRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, str]] = []
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    reply: Optional[str] = None
    action: str = Field(..., description="Action to take: 'engage', 'ignore', 'continue', 'session_ended'")
    metadata: Optional[Dict[str, Any]] = None
