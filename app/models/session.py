from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SessionData(BaseModel):
    """
    Session data model storing conversation state and metadata.
    """
    # Core Identity
    session_id: str = Field(..., alias="sessionId")
    status: str = Field("active", description="active, completed, ended")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Conversation State
    turn_count: int = 0
    conversation_history: List[Dict[str, Any]] = []
    
    # Phase 2: Detection Metadata
    scam_detected: bool = False
    
    # Detection details (Optional until detection happens)
    detection_mode: Optional[str] = None  # 'normal' or 'strict'
    detected_language: Optional[str] = None
    language_confidence: Optional[float] = None
    
    # Classification details
    category: Optional[str] = None
    scam_type: Optional[str] = None
    confidence: Optional[float] = 0.0
    reasoning: Optional[str] = None
    red_flags: List[str] = []
    
    # Phase 3: Engagement State
    stage: str = "monitoring"  # monitoring, engagement, finalization
    
    # Phase 4: Intelligence
    extracted_intel: Dict[str, Any] = {}
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
