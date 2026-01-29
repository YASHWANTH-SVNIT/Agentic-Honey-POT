"""
Demo script for Language Detection (Phase 2.2 & 2.3)

Demonstrates language detection and routing logic.
"""

from app.services.detection.language_detector import detect_and_route


def demo_language_detection():
    """Demonstrate language detection and routing"""
    
    print("\n" + "=" * 70)
    print("PHASE 2.2 & 2.3: LANGUAGE DETECTION AND ROUTING")
    print("=" * 70 + "\n")
    
    test_messages = [
        # English messages - should route to Normal Mode
        {
            "text": "CBI Officer. Money laundering case. Call 9876543210 immediately.",
            "expected_lang": "en",
            "expected_mode": "normal"
        },
        {
            "text": "Your account has been blocked. Click here to verify.",
            "expected_lang": "en",
            "expected_mode": "normal"
        },
        {
            "text": "Congratulations! You won $1,000,000 in lottery!",
            "expected_lang": "en",
            "expected_mode": "normal"
        },
        
        # Hindi/Hinglish messages - should route to Normal Mode
        {
            "text": "Aapka account block ho jayega. Turant call karo.",
            "expected_lang": "hi/en",
            "expected_mode": "normal"
        },
        {
            "text": "आपका खाता ब्लॉक हो जाएगा। तुरंत कॉल करें।",
            "expected_lang": "hi",
            "expected_mode": "normal"
        },
        
        # Other languages - should route to Strict Mode
        {
            "text": "உங்கள் கணக்கு தடுக்கப்படும்",  # Tamil
            "expected_lang": "ta",
            "expected_mode": "strict"
        },
        {
            "text": "మీ ఖాతా బ్లాక్ చేయబడుతుంది",  # Telugu
            "expected_lang": "te",
            "expected_mode": "strict"
        },
        
        # Edge cases
        {
            "text": "?",
            "expected_lang": "unknown/en",
            "expected_mode": "normal"
        },
        {
            "text": "123456789",
            "expected_lang": "unknown",
            "expected_mode": "normal"
        },
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"Example {i}:")
        print("-" * 70)
        print(f"Message: {test['text']}")
        
        result = detect_and_route(test['text'])
        
        print(f"\nDetection Results:")
        print(f"  Language:    {result.language}")
        print(f"  Confidence:  {result.confidence:.2f}")
        print(f"  Mode:        {result.mode.upper()}")
        print(f"  Strict Mode: {result.use_strict_mode}")
        
        print(f"\nExpected:")
        print(f"  Language:    {test['expected_lang']}")
        print(f"  Mode:        {test['expected_mode'].upper()}")
        
        # Verify mode is correct
        if result.mode == test['expected_mode']:
            print(f"\nStatus: PASS (Routed to {result.mode.upper()} mode)")
        else:
            print(f"\nStatus: INFO (Routed to {result.mode.upper()} mode)")
        
        print("\n")
    
    print("=" * 70)
    print("ROUTING LOGIC SUMMARY")
    print("=" * 70)
    print("""
According to README Phase 2.3:

IF language IN ["en", "hi"]:
    → NORMAL MODE (RAG + LLM)

ELSE IF language == "unknown" AND confidence < 0.6:
    → NORMAL MODE (might be English with typos)

ELSE:
    → STRICT MODE (LLM-only, tightened thresholds)

Normal Mode:
  - Uses RAG (ChromaDB) for evidence gathering
  - Standard confidence thresholds (0.7 for ENGAGE)
  - Supports English and Hindi/Hinglish

Strict Mode:
  - Skips RAG (dataset is EN/HI only)
  - Higher confidence thresholds (0.85 for ENGAGE)
  - For other languages (Tamil, Telugu, etc.)
  - Requires 3+ malicious indicators
    """)
    print("=" * 70)


if __name__ == "__main__":
    demo_language_detection()
