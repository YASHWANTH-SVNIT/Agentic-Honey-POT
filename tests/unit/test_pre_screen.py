"""
Unit tests for Pre-Screening Filter (Phase 2.1)

Tests all validation checks according to README specifications.
"""

import pytest
from app.models.schemas import Message, MessageRequest
from app.services.detection.pre_screen import PreScreenFilter, pre_screen_message, PreScreenResult


class TestPreScreenFilter:
    """Test suite for PreScreenFilter"""
    
    def test_valid_message_passes(self):
        """Valid message should pass pre-screening"""
        request = MessageRequest(
            sessionId="test-001",
            message=Message(
                sender="scammer",
                text="CBI Officer. Money laundering case. Call immediately.",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[],
            metadata={"channel": "SMS"}
        )
        
        result = PreScreenFilter.validate(request)
        assert result.passed is True
        assert result.reason is None
    
    def test_null_message_fails(self):
        """Null message should fail - Pydantic will catch this before pre-screening"""
        # Pydantic validation will prevent null message from being created
        # This test verifies that behavior
        with pytest.raises(Exception):  # Pydantic ValidationError
            request = MessageRequest(
                sessionId="test-002",
                message=None,
                conversationHistory=[]
            )
    
    def test_null_text_fails(self):
        """Message with null text should fail - Pydantic will catch this"""
        # Pydantic validation will prevent null text from being created
        # This test verifies that behavior
        with pytest.raises(Exception):  # Pydantic ValidationError
            request = MessageRequest(
                sessionId="test-003",
                message=Message(
                    sender="scammer",
                    text=None,
                    timestamp="2026-01-29T20:00:00Z"
                ),
                conversationHistory=[]
            )
    
    def test_empty_string_fails(self):
        """Empty string text should fail"""
        request = MessageRequest(
            sessionId="test-004",
            message=Message(
                sender="scammer",
                text="",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        result = PreScreenFilter.validate(request)
        assert result.passed is False
        assert "empty" in result.reason.lower()
    
    def test_whitespace_only_fails(self):
        """Whitespace-only text should fail"""
        request = MessageRequest(
            sessionId="test-005",
            message=Message(
                sender="scammer",
                text="   \n\t  ",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        result = PreScreenFilter.validate(request)
        assert result.passed is False
        assert "whitespace" in result.reason.lower()
    
    def test_non_string_text_fails(self):
        """Non-string text should fail"""
        # This test requires bypassing Pydantic validation
        # In practice, Pydantic will catch this, but we test the logic
        request = MessageRequest(
            sessionId="test-006",
            message=Message(
                sender="scammer",
                text="123",  # Will be string due to Pydantic
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        # Manually set to non-string to test the check
        request.message.text = 123
        
        result = PreScreenFilter.validate(request)
        assert result.passed is False
        assert "not a string" in result.reason
    
    def test_should_ignore_convenience_method(self):
        """Test should_ignore convenience method"""
        # Valid message
        valid_request = MessageRequest(
            sessionId="test-007",
            message=Message(
                sender="scammer",
                text="Valid message",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        should_ignore, reason = PreScreenFilter.should_ignore(valid_request)
        assert should_ignore is False
        assert reason is None
        
        # Invalid message
        invalid_request = MessageRequest(
            sessionId="test-008",
            message=Message(
                sender="scammer",
                text="",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        should_ignore, reason = PreScreenFilter.should_ignore(invalid_request)
        assert should_ignore is True
        assert reason is not None
    
    def test_pre_screen_message_function(self):
        """Test standalone pre_screen_message function"""
        request = MessageRequest(
            sessionId="test-009",
            message=Message(
                sender="scammer",
                text="Test message",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        result = pre_screen_message(request)
        assert isinstance(result, PreScreenResult)
        assert result.passed is True
    
    def test_result_boolean_conversion(self):
        """Test PreScreenResult can be used in boolean context"""
        passed_result = PreScreenResult(True)
        failed_result = PreScreenResult(False, "Some reason")
        
        assert bool(passed_result) is True
        assert bool(failed_result) is False
        
        # Can use in if statements
        if passed_result:
            assert True
        else:
            pytest.fail("Should have passed")
        
        if not failed_result:
            assert True
        else:
            pytest.fail("Should have failed")
    
    def test_message_with_special_characters_passes(self):
        """Messages with special characters should pass"""
        request = MessageRequest(
            sessionId="test-010",
            message=Message(
                sender="scammer",
                text="🚨 URGENT! 💰 Pay ₹50,000 NOW! 📞 Call: +91-9876543210",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        result = PreScreenFilter.validate(request)
        assert result.passed is True
    
    def test_message_with_unicode_passes(self):
        """Messages with Unicode (Hindi, Tamil, etc.) should pass"""
        request = MessageRequest(
            sessionId="test-011",
            message=Message(
                sender="scammer",
                text="आपका खाता ब्लॉक हो जाएगा",  # Hindi
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        result = PreScreenFilter.validate(request)
        assert result.passed is True
    
    def test_single_character_message_passes(self):
        """Single character messages should pass"""
        request = MessageRequest(
            sessionId="test-012",
            message=Message(
                sender="scammer",
                text="?",
                timestamp="2026-01-29T20:00:00Z"
            ),
            conversationHistory=[]
        )
        
        result = PreScreenFilter.validate(request)
        assert result.passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
