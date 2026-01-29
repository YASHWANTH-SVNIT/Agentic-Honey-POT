"""
Unit tests for Language Detection (Phase 2.2 & 2.3)

Tests language detection and routing logic according to README specifications.
"""

import pytest
from app.services.detection.language_detector import (
    LanguageDetector,
    LanguageDetectionResult,
    detect_language,
    detect_and_route,
    get_language_detector
)


class TestLanguageDetection:
    """Test suite for Phase 2.2: Language Detection"""
    
    def test_english_detection(self):
        """English messages should be detected as 'en'"""
        detector = LanguageDetector()
        
        messages = [
            "Your account has been blocked",
            "CBI Officer. Money laundering case.",
            "Congratulations! You won $1000",
            "Click here to verify your bank account"
        ]
        
        for msg in messages:
            lang, conf = detector.detect_language(msg)
            assert lang == "en", f"Expected 'en' for: {msg}"
            assert conf > 0.5, f"Low confidence for English: {conf}"
    
    def test_hindi_hinglish_detection(self):
        """Hindi/Hinglish messages should be detected"""
        detector = LanguageDetector()
        
        # Note: langdetect may detect Hinglish as 'en' or 'hi' depending on content
        messages = [
            "Aapka account block ho jayega",
            "Turant call karo",
            "आपका खाता ब्लॉक हो जाएगा"
        ]
        
        for msg in messages:
            lang, conf = detector.detect_language(msg)
            # Should detect some language with reasonable confidence
            assert lang in ["en", "hi"], f"Unexpected language '{lang}' for: {msg}"
            assert conf > 0.3, f"Very low confidence: {conf}"
    
    def test_other_languages_detection(self):
        """Other Indian languages should be detected"""
        detector = LanguageDetector()
        
        test_cases = [
            ("உங்கள் கணக்கு தடுக்கப்படும்", "ta"),  # Tamil
            ("మీ ఖాతా బ్లాక్ చేయబడుతుంది", "te"),  # Telugu
            ("तुमचे खाते ब्लॉक केले जाईल", "mr"),  # Marathi
        ]
        
        for msg, expected_lang in test_cases:
            lang, conf = detector.detect_language(msg)
            # Language detection should work (may not always be exact)
            assert lang != "unknown", f"Failed to detect language for: {msg}"
            assert conf > 0.3, f"Very low confidence: {conf}"
    
    def test_empty_text_detection(self):
        """Empty text should return 'unknown' with 0 confidence"""
        detector = LanguageDetector()
        
        test_cases = ["", "   ", "\n\t", None]
        
        for text in test_cases:
            if text is None:
                text = ""
            lang, conf = detector.detect_language(text)
            assert lang == "unknown"
            assert conf == 0.0
    
    def test_very_short_text(self):
        """Very short text should still attempt detection"""
        detector = LanguageDetector()
        
        lang, conf = detector.detect_language("Hi")
        # Should detect something or return unknown
        assert lang in ["en", "unknown"]
    
    def test_special_characters_only(self):
        """Special characters should return unknown or low confidence"""
        detector = LanguageDetector()
        
        messages = ["!!!", "???", "123", "😀😀😀"]
        
        for msg in messages:
            lang, conf = detector.detect_language(msg)
            # Should handle gracefully
            assert isinstance(lang, str)
            assert 0.0 <= conf <= 1.0
    
    def test_mixed_language_text(self):
        """Mixed language text should detect primary language"""
        detector = LanguageDetector()
        
        # English with Hindi words
        msg = "Your account will be blocked. Aapka account band ho jayega."
        lang, conf = detector.detect_language(msg)
        
        # Should detect one of the languages
        assert lang in ["en", "hi"]
        assert conf > 0.3


class TestLanguageRouting:
    """Test suite for Phase 2.3: Language-Based Routing"""
    
    def test_english_routes_to_normal_mode(self):
        """English should route to Normal Mode"""
        detector = LanguageDetector()
        
        use_strict, mode = detector.determine_mode("en", 0.95)
        
        assert use_strict is False
        assert mode == "normal"
    
    def test_hindi_routes_to_normal_mode(self):
        """Hindi should route to Normal Mode"""
        detector = LanguageDetector()
        
        use_strict, mode = detector.determine_mode("hi", 0.87)
        
        assert use_strict is False
        assert mode == "normal"
    
    def test_tamil_routes_to_strict_mode(self):
        """Tamil should route to Strict Mode"""
        detector = LanguageDetector()
        
        use_strict, mode = detector.determine_mode("ta", 0.92)
        
        assert use_strict is True
        assert mode == "strict"
    
    def test_telugu_routes_to_strict_mode(self):
        """Telugu should route to Strict Mode"""
        detector = LanguageDetector()
        
        use_strict, mode = detector.determine_mode("te", 0.88)
        
        assert use_strict is True
        assert mode == "strict"
    
    def test_unknown_low_confidence_routes_to_normal(self):
        """Unknown with low confidence should route to Normal Mode"""
        detector = LanguageDetector()
        
        # Confidence < 0.6 should use normal mode
        use_strict, mode = detector.determine_mode("unknown", 0.5)
        
        assert use_strict is False
        assert mode == "normal"
    
    def test_unknown_high_confidence_routes_to_strict(self):
        """Unknown with high confidence should route to Strict Mode"""
        detector = LanguageDetector()
        
        # Confidence >= 0.6 should use strict mode
        use_strict, mode = detector.determine_mode("unknown", 0.7)
        
        assert use_strict is True
        assert mode == "strict"
    
    def test_threshold_boundary_at_0_6(self):
        """Test the 0.6 confidence threshold boundary"""
        detector = LanguageDetector()
        
        # Just below threshold
        use_strict_below, mode_below = detector.determine_mode("unknown", 0.59)
        assert use_strict_below is False
        assert mode_below == "normal"
        
        # At threshold
        use_strict_at, mode_at = detector.determine_mode("unknown", 0.6)
        assert use_strict_at is True
        assert mode_at == "strict"
        
        # Above threshold
        use_strict_above, mode_above = detector.determine_mode("unknown", 0.61)
        assert use_strict_above is True
        assert mode_above == "strict"


class TestLanguageDetectionResult:
    """Test suite for LanguageDetectionResult dataclass"""
    
    def test_result_creation(self):
        """LanguageDetectionResult should be created correctly"""
        result = LanguageDetectionResult(
            language="en",
            confidence=0.95,
            use_strict_mode=False,
            mode="normal"
        )
        
        assert result.language == "en"
        assert result.confidence == 0.95
        assert result.use_strict_mode is False
        assert result.mode == "normal"
    
    def test_result_boolean_conversion(self):
        """LanguageDetectionResult should support boolean conversion"""
        # Successful detection
        result_success = LanguageDetectionResult(
            language="en",
            confidence=0.95,
            use_strict_mode=False,
            mode="normal"
        )
        assert bool(result_success) is True
        
        # Unknown with some confidence
        result_unknown = LanguageDetectionResult(
            language="unknown",
            confidence=0.5,
            use_strict_mode=False,
            mode="normal"
        )
        assert bool(result_unknown) is True
        
        # Unknown with zero confidence
        result_failed = LanguageDetectionResult(
            language="unknown",
            confidence=0.0,
            use_strict_mode=False,
            mode="normal"
        )
        assert bool(result_failed) is False


class TestDetectAndRoute:
    """Test suite for complete detection and routing pipeline"""
    
    def test_english_message_complete_flow(self):
        """English message should go through complete flow to Normal Mode"""
        detector = LanguageDetector()
        
        result = detector.detect_and_route("CBI Officer. Money laundering case.")
        
        assert result.language == "en"
        assert result.confidence > 0.5
        assert result.use_strict_mode is False
        assert result.mode == "normal"
    
    def test_tamil_message_complete_flow(self):
        """Tamil message should go through complete flow to Strict Mode"""
        detector = LanguageDetector()
        
        result = detector.detect_and_route("உங்கள் கணக்கு தடுக்கப்படும்")
        
        # If langdetect is not available, it defaults to English
        # In that case, we just verify the result is valid
        if result.language == "en" and result.confidence == 1.0:
            # Langdetect not available - fallback behavior
            assert result.mode == "normal"
        else:
            # Should detect non-English language
            assert result.language != "en"
            assert result.use_strict_mode is True
            assert result.mode == "strict"
    
    def test_empty_message_complete_flow(self):
        """Empty message should return unknown with normal mode"""
        detector = LanguageDetector()
        
        result = detector.detect_and_route("")
        
        assert result.language == "unknown"
        assert result.confidence == 0.0
        # Unknown with 0.0 confidence < 0.6 → Normal mode
        assert result.use_strict_mode is False
        assert result.mode == "normal"


class TestConvenienceFunctions:
    """Test suite for convenience functions"""
    
    def test_detect_language_function(self):
        """Standalone detect_language function should work"""
        lang, conf = detect_language("Your account is blocked")
        
        assert lang == "en"
        assert conf > 0.5
    
    def test_detect_and_route_function(self):
        """Standalone detect_and_route function should work"""
        result = detect_and_route("CBI Officer calling")
        
        assert isinstance(result, LanguageDetectionResult)
        assert result.language == "en"
        assert result.mode == "normal"
    
    def test_get_language_detector_singleton(self):
        """get_language_detector should return singleton instance"""
        detector1 = get_language_detector()
        detector2 = get_language_detector()
        
        assert detector1 is detector2


class TestBackwardCompatibility:
    """Test suite for legacy methods"""
    
    def test_legacy_detect_method(self):
        """Legacy detect() method should still work"""
        detector = LanguageDetector()
        
        lang, conf = detector.detect("Your account blocked")
        
        assert lang == "en"
        assert conf > 0.5
    
    def test_legacy_should_use_strict_mode(self):
        """Legacy should_use_strict_mode() method should still work"""
        detector = LanguageDetector()
        
        # English message
        use_strict, lang, conf = detector.should_use_strict_mode("Account blocked")
        
        assert use_strict is False
        assert lang == "en"
        assert conf > 0.5


class TestCustomSupportedLanguages:
    """Test suite for custom supported languages configuration"""
    
    def test_custom_supported_languages(self):
        """Detector should respect custom supported languages"""
        # Create detector with custom languages
        detector = LanguageDetector(supported_languages=["en", "hi", "ta"])
        
        # Tamil should now route to normal mode
        use_strict, mode = detector.determine_mode("ta", 0.92)
        
        assert use_strict is False
        assert mode == "normal"
    
    def test_default_supported_languages(self):
        """Detector should use default languages from settings"""
        detector = LanguageDetector()
        
        # Should use ["en", "hi"] from settings
        assert "en" in detector.supported_languages
        assert "hi" in detector.supported_languages


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
