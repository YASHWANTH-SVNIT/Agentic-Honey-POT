"""
Quick diagnostic to find where the system is stuck
"""
import sys
sys.path.append(".")

import asyncio
from datetime import datetime

print("\n🔍 DIAGNOSTIC TEST - Finding the bottleneck\n")

# Test 1: Settings
print("1️⃣ Testing settings...")
try:
    import settings
    print(f"   ✅ Settings loaded")
    print(f"   - GROQ_API_KEY: {settings.GROQ_API_KEY[:10]}...")
    print(f"   - LLM_PROVIDER: {settings.LLM_PROVIDER}")
except Exception as e:
    print(f"   ❌ Settings error: {e}")
    exit(1)

# Test 2: LLM Client
print("\n2️⃣ Testing LLM client...")
try:
    from app.services.llm.client import get_llm_client
    client = get_llm_client()
    print(f"   ✅ LLM client initialized")
    
    # Quick test
    start = datetime.now()
    response = client.generate("Say 'test' in one word:", temperature=0.1, max_tokens=10)
    duration = (datetime.now() - start).total_seconds()
    print(f"   ✅ LLM responds in {duration:.2f}s: '{response}'")
except Exception as e:
    print(f"   ❌ LLM client error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Vector Store / RAG
print("\n3️⃣ Testing vector store...")
try:
    from app.services.rag.vector_store import get_vector_store
    vs = get_vector_store()
    print(f"   ✅ Vector store initialized")
    
    # Quick query (this will trigger model loading on first call)
    print(f"   ⏳ Loading embedding model (this takes 3-5s on first query)...")
    start = datetime.now()
    results = vs.search("test", top_k=2)  # Changed from query() to search()
    duration = (datetime.now() - start).total_seconds()
    print(f"   ✅ RAG query in {duration:.2f}s: {len(results)} results")
except Exception as e:
    print(f"   ⚠️  Vector store warning: {e}")
    print(f"   (This is OK if ChromaDB not initialized yet)")

# Test 4: Language Detection
print("\n4️⃣ Testing language detection...")
try:
    from app.services.detection.language_detector import detect_and_route
    result = detect_and_route("Hello this is a test", None)
    print(f"   ✅ Language detected: {result.language} (supported: {result.supported})")
except Exception as e:
    print(f"   ❌ Language detection error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: LLM Detector (the likely culprit)
print("\n5️⃣ Testing LLM detector (LIKELY BOTTLENECK)...")
try:
    from app.services.detection.llm_detector import detect_scam_normal_mode
    from app.services.detection.rag_retriever import retrieve_rag_evidence
    
    test_message = "This is CBI officer. Your Aadhaar linked to money laundering."
    
    print(f"   Getting RAG evidence...")
    start = datetime.now()
    rag_result = retrieve_rag_evidence(test_message)
    rag_duration = (datetime.now() - start).total_seconds()
    print(f"   ✅ RAG done in {rag_duration:.2f}s: {len(rag_result.matches)} matches")
    
    print(f"   Calling LLM detector (this might take 5-10s)...")
    start = datetime.now()
    detection = detect_scam_normal_mode(test_message, rag_result, "en")
    llm_duration = (datetime.now() - start).total_seconds()
    print(f"   ✅ LLM detection done in {llm_duration:.2f}s")
    print(f"   - is_scam: {detection.is_scam}")
    print(f"   - confidence: {detection.confidence}")
    
except Exception as e:
    print(f"   ❌ LLM detector error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 6: Full Pipeline
print("\n6️⃣ Testing full detection pipeline...")
try:
    from app.services.detection.pipeline import get_detection_pipeline
    from app.models.schemas import MessageRequest, Message
    
    pipeline = get_detection_pipeline()
    
    request = MessageRequest(
        sessionId="diagnostic-test",
        message=Message(
            sender="scammer",
            text="Hello",
            timestamp=datetime.now().isoformat()
        ),
        conversationHistory=[],
        metadata={"language": "en"}
    )
    
    print(f"   Running pipeline...")
    start = datetime.now()
    result = asyncio.run(pipeline.process(request))
    duration = (datetime.now() - start).total_seconds()
    print(f"   ✅ Pipeline completed in {duration:.2f}s")
    print(f"   - Action: {result.get('action')}")
    
except Exception as e:
    print(f"   ❌ Pipeline error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*50)
print("✅ ALL DIAGNOSTICS PASSED!")
print("="*50)
print("\n💡 If test_full_system.py still hangs:")
print("   1. The LLM detector might be very slow (5-10s per message)")
print("   2. Check GROQ_API_KEY is valid")
print("   3. Try running with fewer test messages")
print("\n")