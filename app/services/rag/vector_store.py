"""
ChromaDB Vector Store for RAG-based scam detection
Handles embedding and similarity search
"""
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json
from pathlib import Path
import settings

class VectorStore:
    """Manages ChromaDB vector store for scam patterns"""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model"""
        # Create persistent client
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(name="scam_patterns")
            print(f"✓ Loaded existing collection: scam_patterns ({collection.count()} patterns)")
        except:
            collection = self.client.create_collection(
                name="scam_patterns",
                metadata={"description": "Scam pattern database for RAG detection"}
            )
            print("✓ Created new collection: scam_patterns")
        
        return collection
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def add_patterns(self, patterns: List[Dict[str, Any]]):
        """Add scam patterns to collection"""
        if self.collection.count() > 0:
            print(f"Collection already has {self.collection.count()} patterns. Skipping load.")
            return self.collection.count()
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for pattern in patterns:
            # Create unique ID
            ids.append(str(pattern.get("id", len(ids))))
            
            # Combine pattern and example for embedding
            text_to_embed = f"{pattern.get('pattern', '')} {pattern.get('example_message', '')}"
            embedding = self.embed_text(text_to_embed)
            embeddings.append(embedding)
            
            # Store metadata
            metadata = {
                "category": pattern.get("category", "unknown"),
                "scam_type": pattern.get("scam_type", "unknown"),
                "intent": pattern.get("intent", ""),
            }
            metadatas.append(metadata)
            
            # Store document text
            documents.append(pattern.get("pattern", ""))
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        print(f"✓ Added {len(patterns)} patterns to ChromaDB")
        return len(patterns)
    
    def query_similar(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Query for similar scam patterns"""
        # Generate query embedding
        query_embedding = self.embed_text(query_text)
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "category": results['metadatas'][0][i].get('category'),
                    "scam_type": results['metadatas'][0][i].get('scam_type'),
                    "pattern": results['documents'][0][i],
                    "similarity": 1 - results['distances'][0][i],  # Convert distance to similarity
                    "intent": results['metadatas'][0][i].get('intent'),
                }
                formatted_results.append(result)
        
        return {
            "query": query_text,
            "matches": formatted_results,
            "count": len(formatted_results)
        }
    
    def load_dataset_from_json(self, json_path: str = "data/scam_dataset.json"):
        """Load scam dataset from JSON file"""
        path = Path(json_path)
        if not path.exists():
            print(f"✗ Dataset file not found: {json_path}")
            return 0
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            patterns = data
        elif isinstance(data, dict):
            patterns = data.get("patterns", [])
        else:
            print(f"✗ Invalid dataset format")
            return 0
        
        return self.add_patterns(patterns)


# Global instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
