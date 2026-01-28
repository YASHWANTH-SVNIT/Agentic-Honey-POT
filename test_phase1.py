"""
Phase 1 Comprehensive Test
Tests all implemented components
"""
import sys
sys.path.insert(0, '.')

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
    sys.exit(0)
else:
    print("\n  [INCOMPLETE] Some tests failed")
    print("  Review errors above")
    sys.exit(1)
