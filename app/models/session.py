from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SessionData(BaseModel):
    """
    Session data model storing conversation state and metadata.
    
    Changes from original:
    - Removed: detection_mode field (no strict mode)
    - Simplified: Only normal mode exists now
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
    
    # Detection details
    detected_language: Optional[str] = None
    language_confidence: Optional[float] = None
    
    # Classification details
    category: Optional[str] = None
    scam_type: Optional[str] = None
    confidence: Optional[float] = 0.0
    reasoning: Optional[str] = None
    red_flags: List[str] = []
    
    # Phase 3: Engagement State
    persona: Optional[str] = None
    stage: str = "monitoring"  # monitoring, engagement, probing, extraction, termination
    
    # Phase 4: Intelligence (AI-extracted)
    extracted_intel: Dict[str, Any] = Field(default_factory=dict)
    
    # Finalization
    reported_to_guvi: bool = False
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
