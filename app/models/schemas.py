from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    sender: str = "user"  # Default if missing
    text: str = ""  # Default if missing
    timestamp: Optional[str] = None

class MessageRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[Dict[str, Any]]] = None  # Allow None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('conversationHistory', pre=True, always=True)
    def default_history(cls, v):
        return v or []
    
    @validator('message', pre=True)
    def parse_message(cls, v):
        # If message is just a string, convert to object
        if isinstance(v, str):
            return {"text": v, "sender": "user"}
        # If it's a dict but missing sender, add it
        if isinstance(v, dict) and 'sender' not in v:
            v['sender'] = 'user'
        return v

class EngagementMetrics(BaseModel):
    engagementDurationSeconds: int = 0
    totalMessagesExchanged: int = 0

class ExtractedIntelligence(BaseModel):
    """
    GUVI-compliant intelligence structure with AI extraction fields.
    
    Changes from original:
    - Added: amounts (monetary values)
    - Added: bankNames (financial institutions mentioned)
    - Added: ifscCodes (bank branch codes)
    """
    bankAccounts: List[str] = Field(default_factory=list, description="9-18 digit account numbers")
    upiIds: List[str] = Field(default_factory=list, description="Payment IDs with @ symbol")
    phishingLinks: List[str] = Field(default_factory=list, description="URLs and domains")
    phoneNumbers: List[str] = Field(default_factory=list, description="10-digit Indian mobile numbers")
    suspiciousKeywords: List[str] = Field(default_factory=list, description="Threat words and red flags")
    
    # NEW FIELDS (AI Extraction)
    amounts: List[str] = Field(default_factory=list, description="Monetary amounts mentioned")
    bankNames: List[str] = Field(default_factory=list, description="Bank names (SBI, HDFC, etc.)")
    ifscCodes: List[str] = Field(default_factory=list, description="IFSC codes for bank branches")
    emailAddresses: List[str] = Field(default_factory=list, description="Email addresses found")

class MessageResponse(BaseModel):
    status: str = Field(..., description="'success' or 'error'")
    scamDetected: bool
    engagementMetrics: EngagementMetrics
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str = ""
    reply: Optional[str] = None
    action: Optional[str] = None
