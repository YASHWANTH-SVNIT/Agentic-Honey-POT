"""
OPTIMIZED Vector Store - Fast initialization
Key: Lazy loads embedding model only when needed
"""
import chromadb
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import settings

# Lazy import of sentence transformers
_SentenceTransformer = None

def get_sentence_transformer():
    """Lazy load SentenceTransformer only when needed."""
    global _SentenceTransformer
    if _SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer as ST
        _SentenceTransformer = ST
    return _SentenceTransformer

class VectorStore:
    def __init__(self):
        # FAST: ChromaDB client
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        # FAST: Get collection
        self.collection = self.client.get_or_create_collection(
            name="scam_patterns",
            metadata={"description": "Scam patterns"}
        )
        print(f"[OK] Loaded/Created collection: scam_patterns ({self.collection.count()} patterns)")
        
        # LAZY: Don't load model yet
        self.embedding_model = None
        self._model_loaded = False
    
    def _ensure_model_loaded(self):
        """Load model only when needed (first query)."""
        if self._model_loaded:
            return
        
        print("[VectorStore] Loading embedding model (3-5s)...")
        import warnings
        warnings.filterwarnings('ignore')
        
        ST = get_sentence_transformer()
        self.embedding_model = ST(settings.EMBEDDING_MODEL, device='cpu')
        self._model_loaded = True
        print("[VectorStore] Model loaded OK")
    
    def embed_text(self, text: str) -> List[float]:
        self._ensure_model_loaded()
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def add_patterns(self, patterns: List[Dict[str, Any]]):
        if self.collection.count() > 0:
            return self.collection.count()
        
        self._ensure_model_loaded()
        
        ids, embeddings, metadatas, documents = [], [], [], []
        
        for i, pattern in enumerate(patterns):
            ids.append(str(pattern.get("id", i)))
            text = f"{pattern.get('pattern', '')} {pattern.get('example_message', '')}"
            embeddings.append(self.embed_text(text))
            metadatas.append({
                "category": pattern.get("category", "unknown"),
                "scam_type": pattern.get("scam_type", "unknown"),
                "intent": pattern.get("intent", ""),
            })
            documents.append(pattern.get("pattern", ""))
        
        # Batch add
        batch_size = 50
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                documents=documents[i:i+batch_size]
            )
        
        return len(patterns)
    
    def query_similar(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        self._ensure_model_loaded()
        
        query_embedding = self.embed_text(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted = []
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted.append({
                    "id": results['ids'][0][i],
                    "category": results['metadatas'][0][i].get('category'),
                    "scam_type": results['metadatas'][0][i].get('scam_type'),
                    "pattern": results['documents'][0][i],
                    "similarity": 1 - results['distances'][0][i],
                    "intent": results['metadatas'][0][i].get('intent'),
                })
        
        return {"query": query_text, "matches": formatted, "count": len(formatted)}
    
    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Used by rag_retriever."""
        result = self.query_similar(query_text, n_results=top_k)
        
        matches = []
        for match in result.get("matches", []):
            matches.append({
                "text": match.get("pattern", ""),
                "metadata": {
                    "id": match.get("id"),
                    "category": match.get("category"),
                    "scam_type": match.get("scam_type"),
                    "intent": match.get("intent")
                },
                "distance": 1.0 - match.get("similarity", 0.0)
            })
        
        return matches
    
    def load_dataset_from_json(self, json_path: str = "data/scam_dataset.json"):
        path = Path(json_path)
        if not path.exists():
            return 0
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        patterns = data if isinstance(data, list) else data.get("patterns", [])
        return self.add_patterns(patterns)


_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store