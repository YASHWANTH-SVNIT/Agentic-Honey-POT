"""
Example usage of Pre-Screening Filter (Phase 2.1)

This demonstrates how to integrate the pre-screening filter
into the detection pipeline.
"""

from app.models.schemas import Message, MessageRequest, MessageResponse
from app.services.detection.pre_screen import pre_screen_message


def example_detection_pipeline(request: MessageRequest) -> MessageResponse:
    """
    Example detection pipeline showing pre-screening integration.
    
    This is a simplified example showing how Phase 2.1 fits into
    the overall detection flow.
    """
    
    # ============================================================
    # PHASE 2.1: PRE-SCREENING
    # ============================================================
    print("=" * 60)
    print("PHASE 2.1: PRE-SCREENING")
    print("=" * 60)
    
    result = pre_screen_message(request)
    
    if not result.passed:
        print(f"❌ Pre-screening FAILED: {result.reason}")
        print("Action: IGNORE")
        return MessageResponse(
            reply=None,
            action="ignore",
            metadata={"pre_screen_reason": result.reason}
        )
    
    print("✅ Pre-screening PASSED")
    print(f"Message text: '{request.message.text}'")
    print()
    
    # ============================================================
    # NEXT PHASES (to be implemented)
    # ============================================================
    print("Next: Phase 2.2 - Language Detection")
    print("Next: Phase 2.3 - Language-Based Routing")
    print("Next: Phase 2.4A/B - RAG + LLM Detection")
    print("Next: Phase 2.5 - Update Session")
    print()
    
    # For now, return a placeholder response
    return MessageResponse(
        reply=None,
        action="continue",
        metadata={
            "pre_screen_passed": True,
            "message_length": len(request.message.text),
            "next_phase": "language_detection"
        }
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRE-SCREENING FILTER EXAMPLES")
    print("=" * 60 + "\n")
    
    # Example 1: Valid scam message
    print("Example 1: Valid Scam Message")
    print("-" * 60)
    request1 = MessageRequest(
        sessionId="demo-001",
        message=Message(
            sender="scammer",
            text="CBI Officer. Money laundering case. Call 9876543210 immediately.",
            timestamp="2026-01-29T20:00:00Z"
        ),
        conversationHistory=[],
        metadata={"channel": "SMS"}
    )
    response1 = example_detection_pipeline(request1)
    print(f"Response: {response1.model_dump_json(indent=2)}")
    print("\n")
    
    # Example 2: Empty message (should be ignored)
    print("Example 2: Empty Message")
    print("-" * 60)
    request2 = MessageRequest(
        sessionId="demo-002",
        message=Message(
            sender="scammer",
            text="",
            timestamp="2026-01-29T20:00:00Z"
        ),
        conversationHistory=[]
    )
    response2 = example_detection_pipeline(request2)
    print(f"Response: {response2.model_dump_json(indent=2)}")
    print("\n")
    
    # Example 3: Whitespace only (should be ignored)
    print("Example 3: Whitespace Only")
    print("-" * 60)
    request3 = MessageRequest(
        sessionId="demo-003",
        message=Message(
            sender="scammer",
            text="   \n\t  ",
            timestamp="2026-01-29T20:00:00Z"
        ),
        conversationHistory=[]
    )
    response3 = example_detection_pipeline(request3)
    print(f"Response: {response3.model_dump_json(indent=2)}")
    print("\n")
    
    # Example 4: Hindi message (should pass)
    print("Example 4: Hindi/Hinglish Message")
    print("-" * 60)
    request4 = MessageRequest(
        sessionId="demo-004",
        message=Message(
            sender="scammer",
            text="Aapka account block ho jayega. Turant call karo 9876543210",
            timestamp="2026-01-29T20:00:00Z"
        ),
        conversationHistory=[]
    )
    response4 = example_detection_pipeline(request4)
    print(f"Response: {response4.model_dump_json(indent=2)}")
    print("\n")
    
    # Example 5: Single character (should pass)
    print("Example 5: Single Character Message")
    print("-" * 60)
    request5 = MessageRequest(
        sessionId="demo-005",
        message=Message(
            sender="scammer",
            text="?",
            timestamp="2026-01-29T20:00:00Z"
        ),
        conversationHistory=[]
    )
    response5 = example_detection_pipeline(request5)
    print(f"Response: {response5.model_dump_json(indent=2)}")
    print("\n")
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Phase 2.1 Pre-Screening is COMPLETE")
    print("✅ All validation checks implemented")
    print("✅ Ready for Phase 2.2 (Language Detection)")
    print("=" * 60)
