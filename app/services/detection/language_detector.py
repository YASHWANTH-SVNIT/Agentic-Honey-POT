"""
Language Detection Service - English Only (No Strict Mode)
"""

from typing import Tuple, Optional
from dataclasses import dataclass

try:
    from langdetect import detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    LangDetectException = Exception


@dataclass
class LanguageDetectionResult:
    language: str
    confidence: float
    supported: bool
    
    def __bool__(self):
        return self.supported


class LanguageDetector:
    def __init__(self):
        if not LANGDETECT_AVAILABLE:
            print("[WARN] langdetect not available, defaulting to English")
        else:
            print("[LanguageDetector] Initialized (English only)")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        if not text or not text.strip():
            return ("unknown", 0.0)
        
        if not LANGDETECT_AVAILABLE:
            return ("en", 1.0)
        
        try:
            langs = detect_langs(text)
            if langs and len(langs) > 0:
                primary_lang = langs[0]
                return (primary_lang.lang, primary_lang.prob)
            else:
                return ("unknown", 0.0)
        except LangDetectException:
            return ("unknown", 0.0)
        except Exception:
            return ("en", 0.5)
    
    def detect_and_route(self, text: str, metadata: dict = None) -> LanguageDetectionResult:
        # Check metadata first
        if metadata and isinstance(metadata, dict):
            metadata_lang = metadata.get('language') or metadata.get('lang')
            if metadata_lang:
                lang_code = str(metadata_lang).lower()[:2]
                is_supported = lang_code == 'en'
                return LanguageDetectionResult(lang_code, 1.0, is_supported)
        
        # Auto-detect
        language, confidence = self.detect_language(text)
        
        # Be LENIENT - accept English or unknown
        is_supported = (language == "en" or language == "unknown" or confidence < 0.7)
        
        # Check for English words if uncertain
        if not is_supported and confidence < 0.8:
            common_english = ['you', 'your', 'is', 'are', 'have', 'will', 'can', 
                            'money', 'account', 'bank', 'pay', 'transfer', 'verify']
            english_word_count = sum(1 for word in common_english if word in text.lower())
            if english_word_count >= 2:
                is_supported = True
                language = "en"
        
        return LanguageDetectionResult(language, confidence, is_supported)


_language_detector: Optional[LanguageDetector] = None

def get_language_detector() -> LanguageDetector:
    global _language_detector
    if _language_detector is None:
        _language_detector = LanguageDetector()
    return _language_detector

def detect_and_route(text: str, metadata: dict = None) -> LanguageDetectionResult:
    return get_language_detector().detect_and_route(text, metadata)
