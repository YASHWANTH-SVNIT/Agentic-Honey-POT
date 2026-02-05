"""
Scammer Behavior Analyzer - Analyzes scammer's tone and behavior from messages
Helps the agent adapt responses based on how the scammer is acting
"""
from typing import Dict, List, Optional
import re


class ScammerBehaviorAnalyzer:
    """Analyzes scammer's messages to determine their tone and behavior"""
    
    # Keywords indicating aggressive/urgent behavior
    AGGRESSIVE_KEYWORDS = [
        "immediately", "now", "urgent", "hurry", "fast", "quick",
        "arrest", "jail", "police", "court", "warrant", "legal action",
        "block", "freeze", "suspend", "cancel", "terminate",
        "last chance", "final warning", "no time", "right now",
        "dont waste time", "stop wasting", "do it now"
    ]
    
    # Keywords indicating patient/professional behavior
    PATIENT_KEYWORDS = [
        "take your time", "no rush", "when you can", "whenever",
        "please", "kindly", "request", "would you", "could you",
        "understand", "help you", "assist", "guide", "explain"
    ]
    
    # Keywords indicating frustration
    FRUSTRATED_KEYWORDS = [
        "why", "what are you doing", "i told you", "already said",
        "listen", "pay attention", "understand?", "got it?",
        "how many times", "again", "repeat", "stupid", "idiot"
    ]
    
    # Keywords indicating payment info in message
    PAYMENT_KEYWORDS = [
        "upi", "gpay", "phonepe", "paytm", "bhim",
        "@", "account", "transfer", "send", "pay",
        "bank", "ifsc", "neft", "rtgs", "imps"
    ]
    
    @classmethod
    def analyze_tone(cls, message: str) -> str:
        """
        Analyze the scammer's tone from their message.
        Returns: "aggressive", "patient", "frustrated", or "neutral"
        """
        message_lower = message.lower()
        
        # Count keyword matches
        aggressive_count = sum(1 for kw in cls.AGGRESSIVE_KEYWORDS if kw in message_lower)
        patient_count = sum(1 for kw in cls.PATIENT_KEYWORDS if kw in message_lower)
        frustrated_count = sum(1 for kw in cls.FRUSTRATED_KEYWORDS if kw in message_lower)
        
        # Check for ALL CAPS (indicates shouting)
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
        if caps_ratio > 0.5:
            aggressive_count += 2
        
        # Check for multiple exclamation marks
        if message.count("!") >= 2:
            aggressive_count += 1
        
        # Determine tone based on counts
        if frustrated_count >= 2:
            return "frustrated"
        elif aggressive_count >= 2:
            return "aggressive"
        elif patient_count >= 2:
            return "patient"
        elif aggressive_count > patient_count:
            return "aggressive"
        elif patient_count > aggressive_count:
            return "patient"
        else:
            return "neutral"
    
    @classmethod
    def detect_urgency(cls, message: str) -> bool:
        """Check if the scammer is creating urgency"""
        message_lower = message.lower()
        urgency_phrases = [
            "immediately", "right now", "urgent", "hurry",
            "last chance", "final", "only", "today", "now or"
        ]
        return any(phrase in message_lower for phrase in urgency_phrases)
    
    @classmethod
    def detect_payment_request(cls, message: str) -> bool:
        """Check if the scammer is requesting payment"""
        message_lower = message.lower()
        return any(kw in message_lower for kw in cls.PAYMENT_KEYWORDS)
    
    @classmethod
    def detect_threat(cls, message: str) -> bool:
        """Check if the scammer is making threats"""
        message_lower = message.lower()
        threat_phrases = [
            "arrest", "jail", "police", "court", "warrant",
            "legal action", "case", "fir", "complaint",
            "block", "freeze", "suspend", "terminate"
        ]
        return any(phrase in message_lower for phrase in threat_phrases)
    
    @classmethod
    def detect_payment_info_given(cls, message: str) -> Dict[str, bool]:
        """Check what payment info the scammer provided in the message"""
        message_lower = message.lower()
        
        return {
            "has_upi": bool(re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z]+', message)),
            "has_phone": bool(re.search(r'\b[6-9]\d{9}\b', message)),
            "has_bank": bool(re.search(r'\b\d{9,18}\b', message)),
            "has_amount": bool(re.search(r'(?:rs\.?|₹|inr)\s*\d+|^\d+(?:,\d+)*(?:k|lakh|lac)?', message_lower))
        }
    
    @classmethod
    def summarize_last_exchange(cls, history: List[Dict[str, str]], last_message: str) -> str:
        """Create a summary of what just happened in the conversation"""
        
        # Analyze the latest message
        tone = cls.analyze_tone(last_message)
        has_urgency = cls.detect_urgency(last_message)
        has_threat = cls.detect_threat(last_message)
        has_payment_request = cls.detect_payment_request(last_message)
        payment_info = cls.detect_payment_info_given(last_message)
        
        # Build summary
        summary_parts = []
        
        # What info was given
        if payment_info["has_upi"]:
            summary_parts.append("Scammer gave a UPI ID")
        if payment_info["has_phone"]:
            summary_parts.append("Scammer gave a phone number")
        if payment_info["has_bank"]:
            summary_parts.append("Scammer gave a bank account number")
        if payment_info["has_amount"]:
            summary_parts.append("Scammer mentioned an amount")
        
        # What they want
        if has_payment_request:
            summary_parts.append("Scammer is asking for payment")
        if has_threat:
            summary_parts.append("Scammer is making threats")
        if has_urgency:
            summary_parts.append("Scammer is creating urgency")
        
        # Tone
        if tone == "aggressive":
            summary_parts.append("Scammer sounds aggressive/demanding")
        elif tone == "frustrated":
            summary_parts.append("Scammer seems frustrated with you")
        elif tone == "patient":
            summary_parts.append("Scammer is being patient/polite")
        
        if not summary_parts:
            summary_parts.append("Scammer is continuing the conversation")
        
        return ". ".join(summary_parts) + "."
    
    @classmethod
    def get_recommended_compliance(cls, tone: str, turn_count: int) -> str:
        """Get recommended compliance level based on scammer tone and turn count"""
        
        # Early turns - more confused/hesitant
        if turn_count <= 2:
            return "confused"
        
        # Aggressive scammer - comply faster
        if tone == "aggressive":
            return "eager"
        
        # Frustrated scammer - show you're trying
        if tone == "frustrated":
            return "eager"
        
        # Patient scammer - can be more hesitant
        if tone == "patient":
            return "hesitant"
        
        # Default
        return "hesitant"
