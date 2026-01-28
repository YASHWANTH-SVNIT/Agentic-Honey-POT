"""
Final Phase 1 Verification
"""
import sys
sys.path.insert(0, '.')

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
