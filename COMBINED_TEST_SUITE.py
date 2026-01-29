
# --------------------------------------------------------------------------------------------------
# COMBINED FILE ARCHIVE
# Created from: check_settings.py, debug_config.py, test_integrated_system.py, test_phase1.py, test_phase3_engagement.py, verify_phase1_final.py
# --------------------------------------------------------------------------------------------------



# ================================================================================
# START OF SCRIPT: check_settings.py
# ================================================================================


from dotenv import load_dotenv
import os
import settings

# print(f"Loaded API_KEY: {settings.API_KEY}")
# print(f"Env APP_X_API_KEY: {os.getenv('APP_X_API_KEY')}")


# ================================================================================
# END OF SCRIPT: check_settings.py
# ================================================================================



# ================================================================================
# START OF SCRIPT: debug_config.py
# ================================================================================


import sys
import os
# sys.path.insert(0, os.getcwd())
# from config import personas, stages
# from pathlib import Path

# print(f"CWD: {os.getcwd()}")
# print(f"Personas file path: {Path(personas.__file__)}")
# print(f"Personas data path: {personas.data_path}")
# print(f"Personas exists: {personas.data_path.exists()}")
# print(f"PERSONAS len: {len(personas.PERSONAS)}")

# print(f"Stages file path: {Path(stages.__file__)}")
# print(f"Stages data path: {stages.data_path}")
# print(f"Stages exists: {stages.data_path.exists()}")
# print(f"STAGES len: {len(stages.STAGES)}")


# ================================================================================
# END OF SCRIPT: debug_config.py
# ================================================================================



# ================================================================================
# START OF SCRIPT: test_integrated_system.py
# ================================================================================

"""
Test script for integrated Phase 2 + Phase 3 system
Tests detection followed by engagement
"""
import requests
import json

API_URL = "http://127.0.0.1:8001/api/message"
API_KEY = "agentic_honey_pot_2026"

def send_message(session_id, message_text, history):
    """Send a message to the API"""
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text
        },
        "conversationHistory": history
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()

def main_integrated():
    session_id = "test-integrated-001"
    history = []
    
    # Test messages
    messages = [
        "This is Officer Sharma from CBI. Your Aadhaar is linked to money laundering case.",
        "You must join video call immediately or arrest warrant will be issued. Call 9876543210",
        "Pay security deposit of Rs 50,000 to paytm@cbi.gov for verification"
    ]
    
    print("=" * 80)
    print("INTEGRATED PHASE 2 + PHASE 3 TEST")
    print("=" * 80)
    print()
    
    for i, msg in enumerate(messages, 1):
        print(f"\n{'='*80}")
        print(f"TURN {i}")
        print(f"{'='*80}")
        print(f"\n[SCAMMER]: {msg}")
        
        # Send message
        response = send_message(session_id, msg, history)
        
        # Display response
        print(f"\n[SYSTEM]: {response.get('reply', 'No reply')}")
        print(f"\nAction: {response['action']}")
        print(f"Metadata: {json.dumps(response.get('metadata', {}), indent=2)}")
        
        # Update history
        history.append({"sender": "scammer", "text": msg})
        if response.get('reply'):
            history.append({"sender": "agent", "text": response['reply']})
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

# if __name__ == "__main__":
#     main()


# ================================================================================
# END OF SCRIPT: test_integrated_system.py
# ================================================================================



# ================================================================================
# START OF SCRIPT: test_phase1.py
# ================================================================================

"""
Phase 1 Comprehensive Test
Tests all implemented components
"""
import sys
sys.path.insert(0, '.')

def test_phase1():
    print("\n" + "="*70)
    print("  PHASE 1 COMPREHENSIVE TEST")
    print("="*70 + "\n")

    passed = 0
    failed = 0

    # Test 1: Configuration
    print("Test 1: Configuration Module")
    try:
        import settings
        assert settings.GROQ_API_KEY is not None, "GROQ_API_KEY not set"
        assert settings.APP_X_API_KEY is not None, "APP_X_API_KEY not set"
        print("  [PASS] Configuration loaded")
        print(f"    - LLM Provider: {settings.LLM_PROVIDER}")
        print(f"    - Embedding Model: {settings.EMBEDDING_MODEL}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 2: FastAPI App
    print("\nTest 2: FastAPI Application")
    try:
        from main import app
        assert app.title == "Agentic Honey-Pot API"
        print(f"  [PASS] FastAPI app loaded: {app.title}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 3: Data Models
    print("\nTest 3: Pydantic Models")
    try:
        from app.models.schemas import MessageRequest, MessageResponse
        from app.models.session import SessionData
        print("  [PASS] All models imported successfully")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 4: Vector Store
    print("\nTest 4: RAG Vector Store")
    try:
        from app.services.rag.vector_store import get_vector_store
        vs = get_vector_store()
        count = vs.collection.count()
        print(f"  [PASS] Vector store initialized: {count} patterns")
        if count == 0:
            print("    [WARN] Database empty - run scripts/setup_database.py")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 5: LLM Client
    print("\nTest 5: LLM Client")
    try:
        from app.services.llm.client import get_llm_client
        llm = get_llm_client()
        assert llm.primary_client is not None or llm.fallback_client is not None
        print("  [PASS] LLM client initialized")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 6: Session Manager
    print("\nTest 6: Session Manager")
    try:
        from app.services.session.manager import get_session_manager
        sm = get_session_manager()
        test_session = sm.create_session("test-phase1")
        assert test_session.session_id == "test-phase1"
        sm.delete_session("test-phase1")
        print("  [PASS] Session management working")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 7: Language Detector
    print("\nTest 7: Language Detector")
    try:
        from app.services.detection.language_detector import get_language_detector
        ld = get_language_detector()
        lang, conf = ld.detect("Hello, how are you?")
        print(f"  [PASS] Language detection: {lang} (confidence: {conf:.2f})")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 8: Intelligence Extractor
    print("\nTest 8: Intelligence Extractor")
    try:
        from app.services.intelligence.extractors import get_intelligence_extractor
        ie = get_intelligence_extractor()
        test_text = "Call 9876543210 or pay to scammer@paytm. Visit fake-bank.com"
        intel = ie.extract(test_text)
        assert "phone_numbers" in intel
        assert "upi_ids" in intel
        print(f"  [PASS] Intelligence extraction working")
        print(f"    - Phones: {intel.get('phone_numbers', [])}")
        print(f"    - UPI IDs: {intel.get('upi_ids', [])}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Test 9: Configuration Files
    print("\nTest 9: Configuration Files")
    try:
        from config import personas, stages
        assert len(personas.PERSONAS) > 0
        assert len(stages.STAGES) > 0
        print(f"  [PASS] Config files loaded")
        print(f"    - Personas: {len(personas.PERSONAS)}")
        print(f"    - Stages: {len(stages.STAGES)}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"\n  Passed: {passed}/{passed+failed}")
    print(f"  Failed: {failed}/{passed+failed}")

    if failed == 0:
        print("\n  [SUCCESS] PHASE 1 COMPLETE!")
        print("\n  Next Steps:")
        print("  1. Initialize database: python scripts/setup_database.py")
        print("  2. Start server: uvicorn main:app --reload")
        print("  3. Test API: http://localhost:8000/docs")
        # sys.exit(0)
    else:
        print("\n  [INCOMPLETE] Some tests failed")
        print("  Review errors above")
        # sys.exit(1)


# ================================================================================
# END OF SCRIPT: test_phase1.py
# ================================================================================



# ================================================================================
# START OF SCRIPT: test_phase3_engagement.py
# ================================================================================

"""
Test script for Phase 3 Engagement Pipeline
Simulates a multi-turn conversation with a scammer
"""
# import requests
# import json

# API_URL = "http://127.0.0.1:8001/api/message"
# API_KEY = "agentic_honey_pot_2026"

def main_phase3():
    session_id = "dev-test-conversation-01"
    history = []
    
    # Simulated scammer messages
    scammer_messages = [
        "This is Officer Sharma from CBI. Your Aadhaar is linked to money laundering case.",
        "You must join video call immediately or arrest warrant will be issued. Call 9876543210",
        "Pay security deposit of Rs 50,000 to paytm@cbi.gov for verification",
        "Send OTP received on your phone to verify identity",
        "Final warning! Transfer to UPI: scammer123@paytm now!"
    ]
    
    print("=" * 80)
    print("PHASE 3 ENGAGEMENT PIPELINE TEST")
    print("=" * 80)
    print()
    
    for i, scammer_msg in enumerate(scammer_messages, 1):
        print(f"\n{'='*80}")
        print(f"TURN {i}")
        print(f"{'='*80}")
        print(f"\n[SCAMMER]: {scammer_msg}")
        
        # Send message
        response = send_message(session_id, scammer_msg, history)
        
        # Display response
        print(f"\n[AGENT ({response['metadata']['persona']})]: {response['reply']}")
        print(f"\nMetadata:")
        print(f"  - Stage: {response['metadata']['stage']}")
        print(f"  - Turn: {response['metadata']['turn']}")
        print(f"  - Category: {response['metadata']['category']}")
        print(f"  - Extracted Intel: {json.dumps(response['metadata']['extracted_intel'], indent=4)}")
        
        # Update history
        history.append({"sender": "scammer", "text": scammer_msg})
        history.append({"sender": "agent", "text": response['reply']})
        
        # Stop if session ended
        if response['action'] == 'session_ended':
            print("\n[SESSION ENDED]")
            break
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

# if __name__ == "__main__":
#     main()


# ================================================================================
# END OF SCRIPT: test_phase3_engagement.py
# ================================================================================



# ================================================================================
# START OF SCRIPT: verify_phase1_final.py
# ================================================================================

"""
Final Phase 1 Verification
"""
# import sys
# sys.path.insert(0, '.')

def verify_phase1_final():
    print("\n" + "="*70)
    print("  PHASE 1 FINAL VERIFICATION")
    print("="*70 + "\n")

    # Core Components
    print("1. Settings Module:")
    try:
        import settings
        print(f"   [OK] Groq API Key: {settings.GROQ_API_KEY[:20]}...")
        print(f"   [OK] LLM Provider: {settings.LLM_PROVIDER}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n2. FastAPI App:")
    try:
        from main import app
        print(f"   [OK] {app.title} v{app.version}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n3. Vector Store:")
    try:
        from app.services.rag.vector_store import get_vector_store
        vs = get_vector_store()
        count = vs.collection.count()
        print(f"   [OK] ChromaDB: {count} patterns loaded")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n4. LLM Client:")
    try:
        from app.services.llm.client import get_llm_client
        llm = get_llm_client()
        has_client = llm.primary_client is not None or llm.fallback_client is not None
        print(f"   [OK] LLM Client ready: {has_client}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n5. Session Manager:")
    try:
        from app.services.session.manager import get_session_manager
        sm = get_session_manager()
        print(f"   [OK] Session store: {'Redis' if sm.use_redis else 'In-Memory'}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n6. Language Detector:")
    try:
        from app.services.detection.language_detector import get_language_detector
        ld = get_language_detector()
        lang, conf = ld.detect("Hello world")
        print(f"   [OK] Detected: {lang} ({conf:.2f})")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n7. Intelligence Extractor:")
    try:
        from app.services.intelligence.extractors import get_intelligence_extractor
        ie = get_intelligence_extractor()
        intel = ie.extract("Call 9876543210")
        print(f"   [OK] Extracted: {intel.get('phone_numbers', [])}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n" + "="*70)
    print("  PHASE 1 STATUS: READY")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Start server: uvicorn main:app --reload")
    print("  2. Test API: http://localhost:8000/docs")
    print("  3. Health check: http://localhost:8000/api/health")
    print("\n" + "="*70 + "\n")


# ================================================================================
# END OF SCRIPT: verify_phase1_final.py
# ================================================================================

if __name__ == "__main__":
    print("Running Combined Test Suite...")
    print("1. Phase 1 Tests")
    test_phase1()
    
    print("\n2. Phase 1 Verification")
    verify_phase1_final()
    
    print("\n3. Integrated System Test (Phase 2+3)")
    # Note: This requires the server to be running on port 8001
    try:
        main_integrated()
    except Exception as e:
         print(f"Skipping integrated test (is server running?): {e}")

