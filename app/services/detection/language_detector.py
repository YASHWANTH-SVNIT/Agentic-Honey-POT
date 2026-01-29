"""
Language Detection Service (Phase 2.2 & 2.3)

This module implements language detection and routing logic according to README:
- Phase 2.2: Detect language using langdetect
- Phase 2.3: Route to Normal Mode (EN/HI) or Strict Mode (other languages)

Routing Logic (from README):
    IF language IN ["en", "hi"]:
        → NORMAL MODE (RAG + LLM)
    
    ELSE IF language == "unknown" AND confidence < 0.6:
        → NORMAL MODE (might be English with typos)
    
    ELSE:
        → STRICT MODE (LLM-only, tightened thresholds)
"""

from typing import Tuple, Optional
from dataclasses import dataclass
import settings

try:
    from langdetect import detect, detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    LangDetectException = Exception


@dataclass
class LanguageDetectionResult:
    """
    Result of language detection.
    
    Attributes:
        language: Detected language code (e.g., 'en', 'hi', 'ta', 'unknown')
        confidence: Confidence score (0.0 to 1.0)
        use_strict_mode: Whether to use strict mode for detection
        mode: Detection mode name ('normal' or 'strict')
    """
    language: str
    confidence: float
    use_strict_mode: bool
    mode: str
    
    def __bool__(self):
        """Allow boolean conversion - True if detection was successful"""
        return self.language != "unknown" or self.confidence > 0.0


class LanguageDetector:
    """
    Detects language and determines detection mode.
    
    Implements Phase 2.2 (Language Detection) and Phase 2.3 (Language-Based Routing)
    from the README specifications.
    """
    
    def __init__(self, supported_languages: Optional[list] = None):
        """
        Initialize language detector.
        
        Args:
            supported_languages: List of supported language codes (default: ["en", "hi"])
        """
        self.supported_languages = supported_languages or settings.SUPPORTED_LANGUAGES
        
        if not LANGDETECT_AVAILABLE:
            print("[WARN] langdetect not available, defaulting to English")
            print("    Install with: pip install langdetect")
        else:
            print(f"[OK] Language detector initialized (supported: {', '.join(self.supported_languages)})")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of text (Phase 2.2).
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (language_code, confidence)
            
        Examples:
            >>> detector.detect_language("Your account blocked")
            ('en', 0.95)
            
            >>> detector.detect_language("Aapka account block ho jayega")
            ('hi', 0.87)
            
            >>> detector.detect_language("உங்கள் கணக்கு தடுக்கப்படும்")
            ('ta', 0.92)
        """
        if not text or not text.strip():
            return ("unknown", 0.0)
        
        if not LANGDETECT_AVAILABLE:
            # Fallback: assume English
            return ("en", 1.0)
        
        try:
            # Get language with confidence using langdetect
            langs = detect_langs(text)
            
            if langs and len(langs) > 0:
                primary_lang = langs[0]
                return (primary_lang.lang, primary_lang.prob)
            else:
                return ("unknown", 0.0)
                
        except LangDetectException as e:
            # langdetect can fail on very short texts or special characters
            print(f"⚠️  Language detection failed: {e}")
            return ("unknown", 0.0)
            
        except Exception as e:
            # Unexpected error - log and default to English with low confidence
            print(f"❌ Unexpected language detection error: {e}")
            return ("en", 0.5)
    
    def determine_mode(self, language: str, confidence: float) -> Tuple[bool, str]:
        """
        Determine detection mode based on language (Phase 2.3).
        
        Implements the routing logic from README Step 2.3:
        - Supported languages (EN/HI) → Normal Mode
        - Unknown with low confidence → Normal Mode (might be English with typos)
        - Other languages → Strict Mode
        
        Args:
            language: Detected language code
            confidence: Detection confidence (0.0 to 1.0)
            
        Returns:
            Tuple of (use_strict_mode, mode_name)
        """
        # Check 1: Supported languages → Normal Mode
        if language in self.supported_languages:
            return (False, "normal")
        
        # Check 2: Unknown with low confidence → Normal Mode
        # (might be English with typos/special characters)
        if language == "unknown" and confidence < 0.6:
            return (False, "normal")
        
        # Check 3: Everything else → Strict Mode
        return (True, "strict")
    
    def detect_and_route(self, text: str) -> LanguageDetectionResult:
        """
        Complete detection and routing pipeline (Phase 2.2 + 2.3).
        
        This is the main method that combines language detection and mode determination.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetectionResult with all detection metadata
            
        Example:
            >>> result = detector.detect_and_route("CBI Officer. Call immediately.")
            >>> print(f"Language: {result.language}, Mode: {result.mode}")
            Language: en, Mode: normal
        """
        # Phase 2.2: Detect language
        language, confidence = self.detect_language(text)
        
        # Phase 2.3: Determine mode
        use_strict_mode, mode = self.determine_mode(language, confidence)
        
        return LanguageDetectionResult(
            language=language,
            confidence=confidence,
            use_strict_mode=use_strict_mode,
            mode=mode
        )
    
    # Legacy methods for backward compatibility
    def detect(self, text: str) -> Tuple[str, float]:
        """Legacy method - use detect_language() instead"""
        return self.detect_language(text)
    
    def should_use_strict_mode(self, text: str) -> Tuple[bool, str, float]:
        """
        Legacy method - use detect_and_route() instead.
        
        Returns: (use_strict, language, confidence)
        """
        result = self.detect_and_route(text)
        return (result.use_strict_mode, result.language, result.confidence)


# ============================================================
# Global Singleton Instance
# ============================================================

_language_detector: Optional[LanguageDetector] = None


def get_language_detector() -> LanguageDetector:
    """
    Get or create global language detector instance.
    
    Returns:
        LanguageDetector: Singleton instance
    """
    global _language_detector
    if _language_detector is None:
        _language_detector = LanguageDetector()
    return _language_detector


# ============================================================
# Convenience Functions
# ============================================================

def detect_language(text: str) -> Tuple[str, float]:
    """
    Convenience function for language detection.
    
    Args:
        text: Text to analyze
        
    Returns:
        Tuple of (language_code, confidence)
    """
    detector = get_language_detector()
    return detector.detect_language(text)


def detect_and_route(text: str) -> LanguageDetectionResult:
    """
    Convenience function for complete detection and routing.
    
    Args:
        text: Text to analyze
        
    Returns:
        LanguageDetectionResult with all metadata
    """
    detector = get_language_detector()
    return detector.detect_and_route(text)
