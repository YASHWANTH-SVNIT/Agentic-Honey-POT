from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    sender: str
    text: str
    timestamp: Optional[str] = None

class MessageRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, str]] = []
    metadata: Optional[Dict[str, Any]] = None

class EngagementMetrics(BaseModel):
    engagementDurationSeconds: int = 0
    totalMessagesExchanged: int = 0

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

class MessageResponse(BaseModel):
    status: str = Field(..., description="'success' or 'error'")
    scamDetected: bool
    engagementMetrics: EngagementMetrics
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str = ""
    reply: Optional[str] = None  # Added to ensure the platform receives the agent's text
    action: Optional[str] = None # Keeping for internal logic flow if needed, but not strictly required by spec
