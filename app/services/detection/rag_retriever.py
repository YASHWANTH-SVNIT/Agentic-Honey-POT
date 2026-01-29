"""
RAG Retriever for Scam Detection (Phase 2.4A - Part 1)

This module retrieves similar scam patterns from ChromaDB vector store
and formats them as evidence for LLM judgment.

According to README Step 2.4A:
1. Embed incoming message using sentence-transformers
2. Query ChromaDB vector database
3. Retrieve top-K=3-5 similar scam patterns
4. Extract: id, category, scam_type, intent, similarity_score
5. Format evidence for LLM
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.services.rag.vector_store import get_vector_store


@dataclass
class RAGMatch:
    """
    A single RAG match result.
    
    Attributes:
        id: Pattern ID from database
        category: Scam category (e.g., 'digital_arrest', 'job_fraud')
        scam_type: Specific scam type (e.g., 'authority_impersonation')
        pattern: Pattern description text
        similarity: Similarity score (0.0 to 1.0)
        intent: Scam intent description
        similarity_level: Human-readable level (HIGH/MEDIUM/LOW)
    """
    id: str
    category: str
    scam_type: str
    pattern: str
    similarity: float
    intent: str
    
    @property
    def similarity_level(self) -> str:
        """Get human-readable similarity level"""
        if self.similarity >= 0.85:
            return "HIGH"
        elif self.similarity >= 0.65:
            return "MEDIUM"
        else:
            return "LOW"


@dataclass
class RAGRetrievalResult:
    """
    Complete RAG retrieval result.
    
    Attributes:
        query: Original query text
        matches: List of RAGMatch objects
        formatted_context: Formatted text for LLM prompt
        top_category: Most likely category based on top match
        has_high_similarity: Whether any match has high similarity (>= 0.85)
    """
    query: str
    matches: List[RAGMatch]
    formatted_context: str
    top_category: Optional[str]
    has_high_similarity: bool


class RAGRetriever:
    """
    Retrieves and formats RAG evidence for scam detection.
    
    This is used in Normal Mode (Phase 2.4A) for English and Hindi messages.
    """
    
    def __init__(self, top_k: int = 5):
        """
        Initialize RAG retriever.
        
        Args:
            top_k: Number of similar patterns to retrieve (default: 5)
        """
        self.top_k = top_k
        self.vector_store = get_vector_store()
    
    def retrieve(self, message_text: str, top_k: Optional[int] = None) -> RAGRetrievalResult:
        """
        Retrieve similar scam patterns for a message.
        
        Args:
            message_text: The incoming message to analyze
            top_k: Number of results to retrieve (overrides default)
            
        Returns:
            RAGRetrievalResult with matches and formatted context
        """
        k = top_k or self.top_k
        
        # Query vector store
        results = self.vector_store.query_similar(message_text, n_results=k)
        
        # Convert to RAGMatch objects
        matches = []
        for match_data in results.get("matches", []):
            match = RAGMatch(
                id=match_data.get("id", "unknown"),
                category=match_data.get("category", "unknown"),
                scam_type=match_data.get("scam_type", "unknown"),
                pattern=match_data.get("pattern", ""),
                similarity=match_data.get("similarity", 0.0),
                intent=match_data.get("intent", "")
            )
            matches.append(match)
        
        # Format context for LLM
        formatted_context = self._format_context(matches)
        
        # Determine top category and high similarity flag
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
        """
        Format RAG matches as context for LLM prompt.
        
        According to README Step 2.4A Sub-step 2, format as:
        
        Knowledge Base Matches:
        
        Match #1 (Similarity: 0.92 - HIGH):
        • Category: digital_arrest
        • Scam Type: authority_impersonation
        • Pattern: Authority impersonates law enforcement...
        
        Args:
            matches: List of RAGMatch objects
            
        Returns:
            Formatted string for LLM prompt
        """
        if not matches:
            return "No similar patterns found in knowledge base."
        
        lines = ["Knowledge Base Matches:", ""]
        
        for i, match in enumerate(matches, 1):
            lines.append(f"Match #{i} (Similarity: {match.similarity:.2f} - {match.similarity_level}):")
            lines.append(f"• Category: {match.category}")
            lines.append(f"• Scam Type: {match.scam_type}")
            lines.append(f"• Pattern: {match.pattern}")
            
            if match.intent:
                lines.append(f"• Intent: {match.intent}")
            
            lines.append("")  # Blank line between matches
        
        return "\n".join(lines)
    
    def get_top_match(self, message_text: str) -> Optional[RAGMatch]:
        """
        Get only the top matching pattern.
        
        Args:
            message_text: The incoming message
            
        Returns:
            Top RAGMatch or None if no matches
        """
        result = self.retrieve(message_text, top_k=1)
        return result.matches[0] if result.matches else None


# ============================================================
# Global Singleton Instance
# ============================================================

_rag_retriever: Optional[RAGRetriever] = None


def get_rag_retriever(top_k: int = 5) -> RAGRetriever:
    """
    Get or create global RAG retriever instance.
    
    Args:
        top_k: Number of results to retrieve
        
    Returns:
        RAGRetriever: Singleton instance
    """
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever(top_k=top_k)
    return _rag_retriever


# ============================================================
# Convenience Functions
# ============================================================

def retrieve_rag_evidence(message_text: str, top_k: int = 5) -> RAGRetrievalResult:
    """
    Convenience function to retrieve RAG evidence.
    
    Args:
        message_text: The incoming message
        top_k: Number of results to retrieve
        
    Returns:
        RAGRetrievalResult with matches and formatted context
    """
    retriever = get_rag_retriever(top_k=top_k)
    return retriever.retrieve(message_text, top_k=top_k)
