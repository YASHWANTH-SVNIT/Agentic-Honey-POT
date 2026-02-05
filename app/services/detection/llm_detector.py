"""
LLM Detector for Scam Detection

This module uses LLM to make final scam judgment using RAG context.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.services.llm.client import get_llm_client
from app.services.detection.rag_retriever import RAGRetrievalResult


@dataclass
class ScamDetectionResult:
    """
    Result of LLM scam detection.
    
    Attributes:
        is_scam: Whether message is classified as scam
        confidence: Confidence score (0.0 to 1.0)
        primary_category: Detected scam category (e.g., 'digital_arrest')
        reasoning: LLM's explanation (2-3 sentences)
        matched_patterns: List of matched scam patterns
        red_flags: List of identified red flags
        legitimacy_indicators: List of legitimacy indicators (if any)
        raw_response: Raw LLM response for debugging
    """
    is_scam: bool
    confidence: float
    primary_category: Optional[str]
    reasoning: str
    matched_patterns: list
    red_flags: list
    legitimacy_indicators: list
    raw_response: Optional[Dict[str, Any]] = None


class LLMDetector:
    """
    Uses LLM to detect scam intent with RAG context.
    """
    
    def __init__(self):
        """Initialize LLM detector"""
        self.llm_client = get_llm_client()
    
    def detect_normal_mode(
        self,
        message_text: str,
        rag_result: RAGRetrievalResult,
        language: str = "en"
    ) -> ScamDetectionResult:
        """
        Detect scam using RAG context + LLM judgment.
        
        Args:
            message_text: The incoming message
            rag_result: RAG retrieval result with evidence
            language: Detected language code
            
        Returns:
            ScamDetectionResult with LLM judgment
        """
        # Build prompt with RAG context
        prompt = self._build_normal_mode_prompt(message_text, rag_result)
        
        # Get LLM response
        try:
            response = self.llm_client.generate_json(prompt, temperature=0.3)
            # Trigger fallback if LLM response indicates an error or no LLM keys
            if response.get("error") or "No LLM keys configured" in str(response.get("reasoning", "")):
                 raise Exception("LLM returned error response or mock")
        except Exception as e:
            print(f"[WARN] LLM fallback triggered: {e}")
            
            # Heuristic Fallback
            is_scam_keywords = ["police", "arrest", "verify", "account", "blocked", "cbi", "aadhaar", "money laundering"]
            is_scam = any(k in message_text.lower() for k in is_scam_keywords)
            
            return ScamDetectionResult(
                is_scam=is_scam,
                confidence=0.95 if is_scam else 0.0,
                primary_category="digital_arrest" if "cbi" in message_text.lower() or "arrest" in message_text.lower() else "heuristic_fallback",
                reasoning="LLM Failed/Mocked - Fallback to keyword matching",
                matched_patterns=["keyword_match"] if is_scam else [],
                red_flags=["High Urgency", "Recall LLM"] if is_scam else [],
                legitimacy_indicators=[],
                raw_response={"fallback": True}
            )
        
        # Parse and return result
        return self._parse_llm_response(response)
    
    def _build_normal_mode_prompt(
        self,
        message_text: str,
        rag_result: RAGRetrievalResult
    ) -> str:
        """
        Build LLM prompt with RAG context.
        """
        prompt = f"""You are a scam detection expert for India.

INCOMING MESSAGE:
"{message_text}"

{rag_result.formatted_context}

ANALYSIS FRAMEWORK:
1. Pattern Matching: Does it match known scam patterns from the knowledge base?
2. Legitimacy Indicators: Official domains, toll-free numbers, transaction IDs?
3. Scam Indicators: Threats, urgency, fake domains, personal contacts?
4. Context: Could there be a legitimate explanation?

RESPOND IN JSON:
{{
  "is_scam": true/false,
  "confidence": 0.0-1.0,
  "primary_category": "category_name" or null,
  "reasoning": "2-3 sentence explanation",
  "matched_patterns": ["pattern1", "pattern2"],
  "red_flags": ["flag1", "flag2"],
  "legitimacy_indicators": ["indicator1"] or []
}}

Be thorough but concise. Focus on evidence from the knowledge base matches."""
        
        return prompt
    
    def _parse_llm_response(
        self,
        response: Dict[str, Any]
    ) -> ScamDetectionResult:
        """
        Parse LLM JSON response into ScamDetectionResult.
        
        Args:
            response: LLM JSON response
            
        Returns:
            ScamDetectionResult
        """
        return ScamDetectionResult(
            is_scam=response.get("is_scam", False),
            confidence=float(response.get("confidence", 0.0)),
            primary_category=response.get("primary_category"),
            reasoning=response.get("reasoning", "No reasoning provided"),
            matched_patterns=response.get("matched_patterns", []),
            red_flags=response.get("red_flags", []),
            legitimacy_indicators=response.get("legitimacy_indicators", []),
            raw_response=response
        )


# ============================================================
# Global Singleton Instance
# ============================================================

_llm_detector: Optional[LLMDetector] = None


def get_llm_detector() -> LLMDetector:
    """
    Get or create global LLM detector instance.
    
    Returns:
        LLMDetector: Singleton instance
    """
    global _llm_detector
    if _llm_detector is None:
        _llm_detector = LLMDetector()
    return _llm_detector


# ============================================================
# Convenience Functions
# ============================================================

def detect_scam_normal_mode(
    message_text: str,
    rag_result: RAGRetrievalResult,
    language: str = "en"
) -> ScamDetectionResult:
    """
    Turn-key function for detection.
    
    Args:
        message_text: The incoming message
        rag_result: RAG retrieval result
        language: Detected language
        
    Returns:
        ScamDetectionResult
    """
    detector = get_llm_detector()
    return detector.detect_normal_mode(message_text, rag_result, language)
