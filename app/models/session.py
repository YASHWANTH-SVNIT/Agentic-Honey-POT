from pydantic import BaseModel
from typing import Dict, Any, Optional

class SessionData(BaseModel):
    sessionId: str
    scam_detected: bool = False
    turn_count: int = 0
    extracted_intel: Dict[str, Any] = {}
    status: str = "active"
