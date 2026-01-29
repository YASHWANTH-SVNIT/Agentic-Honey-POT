"""
Integration Test: Phase 1 (RAG) + Phase 2 (Detection Pipeline)

Verifies the complete flow from Data Loading -> RAG Retrieval -> Pipeline Processing -> Session Update.
This runs the ACTUAL system components, not mocks.

Prerequisites:
- .env file with API keys (GROQ_API_KEY or GOOGLE_API_KEY)
- data/scam_dataset.json should exist
"""

import sys
import os
import asyncio
from pathlib import Path
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.services.rag.vector_store import get_vector_store
    from app.services.detection.pipeline import get_detection_pipeline
    from app.models.schemas import MessageRequest, Message
    from app.services.session.manager import get_session_manager
    import settings
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running this from the project root or scripts directory.")
    sys.exit(1)


async def run_integration_test():
    print("\n" + "="*80)
    print("PHASE 1 & 2 INTEGRATION TEST")
    print("="*80 + "\n")
    
    # ---------------------------------------------------------
    # PART 1: Initialize Phase 1 (Vector Store & Data)
    # ---------------------------------------------------------
    print("[STEP 1]: Initializing Vector Store (Phase 1)...")
    vector_store = get_vector_store()
    
    # Load dataset
    print("   Loading dataset from data/scam_dataset.json...")
    count = vector_store.load_dataset_from_json("data/scam_dataset.json")
    print(f"   [OK] Vector Store ready with {count} patterns.")
    
    # Verify retrieval works
    test_query = "CBI officer calling regarding money laundering"
    results = vector_store.query_similar(test_query, n_results=1)
    if results['matches']:
        top_match = results['matches'][0]
        print(f"   [OK] Retrieval Verified: Query '{test_query[:20]}...' matched category '{top_match['category']}' ({top_match['similarity']:.2f})")
    else:
        print("   [WARN] Retrieval returned no matches. Dataset might be empty.")

    # ---------------------------------------------------------
    # PART 2: Check LLM Configuration
    # ---------------------------------------------------------
    print("\n[STEP 2]: Checking LLM Configuration...")
    if settings.GROQ_API_KEY:
        print("   [OK] GROQ_API_KEY found.")
    elif settings.GOOGLE_API_KEY:
        print("   [OK] GOOGLE_API_KEY found.")
    else:
        print("   [WARN] NO API KEYS FOUND! LLM detection may fail or return defaults.")

    # ---------------------------------------------------------
    # PART 3: Initialize Phase 2 (Detection Pipeline)
    # ---------------------------------------------------------
    print("\n[STEP 3]: Initializing Detection Pipeline (Phase 2)...")
    pipeline = get_detection_pipeline()
    session_manager = get_session_manager()
    
    # ---------------------------------------------------------
    # PART 4: Run Real Scam Scenario
    # ---------------------------------------------------------
    scam_msg = "Hello sir, I am calling from Mumbai Police. Your Aadhaar card is linked to illegal money laundering activity. You must verify immediately or you will be arrested in 1 hour. Video call me now."
    session_id = "test_integration_001"
    
    print("\n[STEP 4]: Processing Scam Message...")
    print(f"   Session ID: {session_id}")
    print(f"   Message: \"{scam_msg}\"")
    print("-" * 40)
    
    # Create request
    request = MessageRequest(
        sessionId=session_id,
        message=Message(sender="scammer", text=scam_msg)
    )
    
    # Run Pipeline
    result = await pipeline.process(request)
    
    print("-" * 40)
    print("   [OK] Pipeline Processing Complete.")
    print(f"   Result Action: {result.get('action').upper()}")
    
    # ---------------------------------------------------------
    # PART 5: Verify Session State (Phase 2.5)
    # ---------------------------------------------------------
    print("\n[STEP 5]: Verifying Session State...")
    session = session_manager.get_session(session_id)
    
    if session:
        print(f"   Session ID: {session.session_id}")
        print(f"   Scam Detected: {session.scam_detected} (Expected: True)")
        print(f"   Stage: {session.stage} (Expected: engagement)")
        print(f"   Detected Category: {session.category}")
        print(f"   Confidence: {session.confidence}")
        print(f"   Language: {session.detected_language}")
        
        if session.scam_detected and session.stage == "engagement":
            print("\n[SUCCESS] System successfully detected scam and transitioned to engagement phase!")
        else:
            print("\n[FAILURE] Session state verification failed.")
    else:
        print("\n[FAILURE] Session not found.")

    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(run_integration_test())
