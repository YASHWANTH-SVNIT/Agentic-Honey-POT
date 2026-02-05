"""
RAG Retriever - FIXED to use vector_store.search()
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.services.rag.vector_store import get_vector_store


@dataclass
class RAGMatch:
    id: str
    category: str
    scam_type: str
    pattern: str
    similarity: float
    intent: str
    
    @property
    def similarity_level(self) -> str:
        if self.similarity >= 0.85:
            return "HIGH"
        elif self.similarity >= 0.65:
            return "MEDIUM"
        else:
            return "LOW"


@dataclass
class RAGRetrievalResult:
    query: str
    matches: List[RAGMatch]
    formatted_context: str
    top_category: Optional[str]
    has_high_similarity: bool


class RAGRetriever:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.vector_store = get_vector_store()
    
    def retrieve(self, message_text: str, top_k: Optional[int] = None) -> RAGRetrievalResult:
        k = top_k or self.top_k
        
        # FIXED: Use search() method
        raw_results = self.vector_store.search(message_text, top_k=k)
        
        matches = []
        for result in raw_results:
            metadata = result.get("metadata", {})
            text = result.get("text", "")
            distance = result.get("distance", 1.0)
            similarity = max(0.0, 1.0 - distance)
            
            match = RAGMatch(
                id=metadata.get("id", "unknown"),
                category=metadata.get("category", "unknown"),
                scam_type=metadata.get("scam_type", metadata.get("category", "unknown")),
                pattern=text[:200],
                similarity=similarity,
                intent=metadata.get("intent", "Scam activity")
            )
            matches.append(match)
        
        formatted_context = self._format_context(matches)
        top_category = matches[0].category if matches else None
        has_high_similarity = any(m.similarity >= 0.85 for m in matches)
        
        return RAGRetrievalResult(
            query=message_text,
            matches=matches,
            formatted_context=formatted_context,
            top_category=top_category,
            has_high_similarity=has_high_similarity
        )
    
    def _format_context(self, matches: List[RAGMatch]) -> str:
        if not matches:
            return "Knowledge Base: None found"
        
        lines = ["KNOWLEDGE BASE MATCHES:"]
        for i, match in enumerate(matches, 1):
            lines.append(f"\nMatch #{i} (Similarity: {match.similarity:.2f} - {match.similarity_level}):")
            lines.append(f"• Category: {match.category}")
            lines.append(f"• Pattern: {match.pattern}")
        
        return "\n".join(lines)


_rag_retriever: Optional[RAGRetriever] = None

def get_rag_retriever(top_k: int = 5) -> RAGRetriever:
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever(top_k=top_k)
    return _rag_retriever

def retrieve_rag_evidence(message: str, top_k: int = 5) -> RAGRetrievalResult:
    retriever = get_rag_retriever(top_k=top_k)
    return retriever.retrieve(message, top_k=top_k)