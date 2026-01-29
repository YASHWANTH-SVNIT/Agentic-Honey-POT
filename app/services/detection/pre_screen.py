"""
Pre-Screening Filter for Incoming Messages

This module implements minimal validation checks on incoming messages
before they enter the detection pipeline. According to the README Phase 2.1,
we ONLY check for null/empty/invalid message structures.

The goal is to filter out obviously invalid messages while allowing
everything else to proceed to the full detection pipeline.
"""

from typing import Optional, Dict, Any
from app.models.schemas import Message, MessageRequest


class PreScreenResult:
    """Result of pre-screening validation"""
    
    def __init__(self, passed: bool, reason: Optional[str] = None):
        self.passed = passed
        self.reason = reason
    
    def __bool__(self):
        return self.passed


class PreScreenFilter:
    """
    Minimal pre-screening filter for incoming messages.
    
    According to README Step 2.1, we ONLY check:
    - message == null → IGNORE
    - message.text == null → IGNORE
    - message.text == "" → IGNORE
    - typeof(message.text) != string → IGNORE
    - message.text.strip() == "" → IGNORE
    
    Everything else passes through to the detection pipeline.
    """
    
    @staticmethod
    def validate(request: MessageRequest) -> PreScreenResult:
        """
        Validate incoming message request.
        
        Args:
            request: MessageRequest object containing the message
            
        Returns:
            PreScreenResult: Object with passed (bool) and reason (str) attributes
        """
        
        # Check 1: message == null
        if request.message is None:
            return PreScreenResult(False, "message is null")
        
        # Check 2: message.text == null
        if request.message.text is None:
            return PreScreenResult(False, "message.text is null")
        
        # Check 3: typeof(message.text) != string
        if not isinstance(request.message.text, str):
            return PreScreenResult(False, f"message.text is not a string (type: {type(request.message.text).__name__})")
        
        # Check 4: message.text == ""
        if request.message.text == "":
            return PreScreenResult(False, "message.text is empty string")
        
        # Check 5: message.text.strip() == ""
        if request.message.text.strip() == "":
            return PreScreenResult(False, "message.text is whitespace only")
        
        # All checks passed
        return PreScreenResult(True)
    
    @staticmethod
    def should_ignore(request: MessageRequest) -> tuple[bool, Optional[str]]:
        """
        Convenience method that returns (should_ignore, reason).
        
        Args:
            request: MessageRequest object
            
        Returns:
            tuple: (bool, str) - (True if should ignore, reason for ignoring)
        """
        result = PreScreenFilter.validate(request)
        return (not result.passed, result.reason)


# Convenience function for direct use
def pre_screen_message(request: MessageRequest) -> PreScreenResult:
    """
    Pre-screen an incoming message request.
    
    Args:
        request: MessageRequest object
        
    Returns:
        PreScreenResult: Validation result
        
    Example:
        >>> result = pre_screen_message(request)
        >>> if not result.passed:
        >>>     return {"reply": None, "action": "ignore"}
    """
    return PreScreenFilter.validate(request)
