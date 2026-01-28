"""
Setup Database - Initialize ChromaDB with scam patterns
"""
import sys
sys.path.insert(0, '.')

from app.services.rag.vector_store import get_vector_store

print("\n" + "="*70)
print("  INITIALIZING CHROMADB DATABASE")
print("="*70 + "\n")

try:
    # Get vector store instance
    vector_store = get_vector_store()
    
    # Load dataset from JSON
    count = vector_store.load_dataset_from_json("data/scam_dataset.json")
    
    print(f"\n✓ DATABASE INITIALIZED SUCCESSFULLY")
    print(f"  Total patterns loaded: {count}")
    
    # Test query
    print("\n" + "="*70)
    print("  TESTING SIMILARITY SEARCH")
    print("="*70 + "\n")
    
    test_query = "CBI officer calling about money laundering case"
    results = vector_store.query_similar(test_query, n_results=3)
    
    print(f"Query: '{test_query}'")
    print(f"\nTop {len(results['matches'])} matches:\n")
    
    for i, match in enumerate(results['matches'], 1):
        print(f"{i}. Category: {match['category']}")
        print(f"   Similarity: {match['similarity']:.3f}")
        print(f"   Pattern: {match['pattern'][:80]}...")
        print()
    
    print("="*70)
    print("✓ SETUP COMPLETE - Database ready for use")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ SETUP FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
