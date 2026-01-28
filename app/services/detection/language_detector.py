"""
Language Detection Service
Detects language and determines detection mode
"""
from typing import Tuple
import settings

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class LanguageDetector:
    """Detects language and determines detection mode"""
    
    def __init__(self):
        """Initialize language detector"""
        if not LANGDETECT_AVAILABLE:
            print("⚠ langdetect not available, defaulting to English")
        else:
            print("✓ Language detector initialized")
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect language of text
        Returns: (language_code, confidence)
        """
        if not LANGDETECT_AVAILABLE:
            return ("en", 1.0)
        
        try:
            # Get language with confidence
            langs = detect_langs(text)
            if langs:
                primary_lang = langs[0]
                return (primary_lang.lang, primary_lang.prob)
            else:
                return ("unknown", 0.0)
        except Exception as e:
            print(f"✗ Language detection error: {e}")
            return ("en", 0.5)  # Default to English with low confidence
    
    def should_use_strict_mode(self, text: str) -> Tuple[bool, str, float]:
        """
        Determine if strict mode should be used
        Returns: (use_strict, language, confidence)
        """
        lang, conf = self.detect(text)
        
        # Use normal mode for supported languages
        if lang in settings.SUPPORTED_LANGUAGES:
            return (False, lang, conf)
        
        # Use normal mode for unknown with low confidence (might be English with typos)
        if lang == "unknown" and conf < 0.6:
            return (False, "en", conf)
        
        # Use strict mode for other languages
        return (True, lang, conf)


# Global instance
_language_detector = None

def get_language_detector() -> LanguageDetector:
    """Get or create global language detector instance"""
    global _language_detector
    if _language_detector is None:
        _language_detector = LanguageDetector()
    return _language_detector
