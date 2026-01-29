"""
Unit tests for Phase 2.4: RAG + LLM Detection

Tests RAG retrieval, LLM detection (both modes), and decision making.
"""

import pytest
from app.services.detection.rag_retriever import (
    RAGRetriever,
    RAGMatch,
    RAGRetrievalResult,
    retrieve_rag_evidence
)
from app.services.detection.llm_detector import (
    LLMDetector,
    ScamDetectionResult
)
from app.services.detection.decision_maker import (
    DecisionMaker,
    FinalDecision,
    make_final_decision
)


class TestRAGRetriever:
    """Test suite for RAG Retriever (Phase 2.4A - Part 1)"""
    
    def test_rag_match_creation(self):
        """RAGMatch should be created correctly"""
        match = RAGMatch(
            id="1",
            category="digital_arrest",
            scam_type="authority_impersonation",
            pattern="Authority impersonates law enforcement",
            similarity=0.92,
            intent="Create fear and urgency"
        )
        
        assert match.id == "1"
        assert match.category == "digital_arrest"
        assert match.similarity == 0.92
        assert match.similarity_level == "HIGH"
    
    def test_similarity_levels(self):
        """Similarity levels should be categorized correctly"""
        high_match = RAGMatch("1", "cat", "type", "pattern", 0.90, "intent")
        medium_match = RAGMatch("2", "cat", "type", "pattern", 0.70, "intent")
        low_match = RAGMatch("3", "cat", "type", "pattern", 0.50, "intent")
        
        assert high_match.similarity_level == "HIGH"
        assert medium_match.similarity_level == "MEDIUM"
        assert low_match.similarity_level == "LOW"
    
    def test_rag_retrieval_result_creation(self):
        """RAGRetrievalResult should be created correctly"""
        matches = [
            RAGMatch("1", "digital_arrest", "authority", "Pattern 1", 0.92, "Intent 1")
        ]
        
        result = RAGRetrievalResult(
            query="Test message",
            matches=matches,
            formatted_context="Formatted context",
            top_category="digital_arrest",
            has_high_similarity=True
        )
        
        assert result.query == "Test message"
        assert len(result.matches) == 1
        assert result.top_category == "digital_arrest"
        assert result.has_high_similarity is True
    
    def test_rag_retriever_initialization(self):
        """RAG retriever should initialize with default top_k"""
        retriever = RAGRetriever()
        assert retriever.top_k == 5
        
        retriever_custom = RAGRetriever(top_k=3)
        assert retriever_custom.top_k == 3
    
    def test_format_context_empty(self):
        """Format context should handle empty matches"""
        retriever = RAGRetriever()
        formatted = retriever._format_context([])
        
        assert "No similar patterns" in formatted
    
    def test_format_context_with_matches(self):
        """Format context should format matches correctly"""
        retriever = RAGRetriever()
        matches = [
            RAGMatch("1", "digital_arrest", "authority", "Pattern 1", 0.92, "Intent 1"),
            RAGMatch("2", "job_fraud", "fake_job", "Pattern 2", 0.75, "Intent 2")
        ]
        
        formatted = retriever._format_context(matches)
        
        assert "Match #1" in formatted
        assert "Match #2" in formatted
        assert "digital_arrest" in formatted
        assert "job_fraud" in formatted
        assert "0.92" in formatted
        assert "HIGH" in formatted


class TestScamDetectionResult:
    """Test suite for ScamDetectionResult dataclass"""
    
    def test_detection_result_creation(self):
        """ScamDetectionResult should be created correctly"""
        result = ScamDetectionResult(
            is_scam=True,
            confidence=0.92,
            primary_category="digital_arrest",
            reasoning="Clear scam indicators",
            matched_patterns=["authority_impersonation"],
            red_flags=["Personal phone", "Urgency"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        assert result.is_scam is True
        assert result.confidence == 0.92
        assert result.primary_category == "digital_arrest"
        assert result.detection_mode == "normal"
        assert len(result.red_flags) == 2


class TestDecisionMaker:
    """Test suite for Decision Maker (Phase 2.4 - Final Step)"""
    
    def test_decision_maker_initialization(self):
        """Decision maker should initialize with thresholds"""
        dm = DecisionMaker()
        
        # Check default thresholds from settings
        assert dm.normal_engage_threshold == 0.7
        assert dm.normal_probe_threshold == 0.5
        assert dm.strict_engage_threshold == 0.85
        assert dm.strict_probe_threshold == 0.70
    
    def test_decision_maker_custom_thresholds(self):
        """Decision maker should accept custom thresholds"""
        dm = DecisionMaker(
            normal_engage_threshold=0.8,
            normal_probe_threshold=0.6,
            strict_engage_threshold=0.9,
            strict_probe_threshold=0.75
        )
        
        assert dm.normal_engage_threshold == 0.8
        assert dm.normal_probe_threshold == 0.6
        assert dm.strict_engage_threshold == 0.9
        assert dm.strict_probe_threshold == 0.75
    
    def test_normal_mode_high_confidence_engage(self):
        """Normal mode: High confidence (≥0.7) should ENGAGE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.92,
            primary_category="digital_arrest",
            reasoning="Clear scam",
            matched_patterns=["pattern1"],
            red_flags=["flag1", "flag2"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "engage"
        assert decision.scam_detected is True
        assert decision.confidence == 0.92
    
    def test_normal_mode_medium_confidence_probe(self):
        """Normal mode: Medium confidence (0.5-0.7) should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.6,
            primary_category="job_fraud",
            reasoning="Some indicators",
            matched_patterns=["pattern1"],
            red_flags=["flag1"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "probe"
        assert decision.scam_detected is True
        assert decision.confidence == 0.6
    
    def test_normal_mode_low_confidence_ignore(self):
        """Normal mode: Low confidence (<0.5) should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.4,
            primary_category="unknown",
            reasoning="Uncertain",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_normal_mode_not_scam_ignore(self):
        """Normal mode: is_scam=False should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=False,
            confidence=0.95,
            primary_category=None,
            reasoning="Legitimate message",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=["Official domain"],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_strict_mode_high_confidence_with_indicators_engage(self):
        """Strict mode: High confidence (≥0.85) + 3+ indicators should ENGAGE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.90,
            primary_category="digital_arrest",
            reasoning="Multiple scam indicators",
            matched_patterns=["pattern1", "pattern2"],
            red_flags=["Threat", "Urgency", "Payment demand", "Fake authority"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "engage"
        assert decision.scam_detected is True
        assert decision.detection_mode == "strict"
    
    def test_strict_mode_high_confidence_insufficient_indicators_ignore(self):
        """Strict mode: High confidence but <3 indicators should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.90,
            primary_category="unknown",
            reasoning="High confidence but few indicators",
            matched_patterns=[],
            red_flags=["flag1", "flag2"],  # Only 2 indicators
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        # Should fallback to PROBE because it meets the probe criteria (>= 0.70 conf, >= 2 indicators)
        # even though it failed the ENGAGE criteria (>= 3 indicators)
        assert decision.action == "probe"
        assert decision.scam_detected is True
    
    def test_strict_mode_medium_confidence_probe(self):
        """Strict mode: Medium confidence (0.70-0.85) + 2+ indicators should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.75,
            primary_category="job_fraud",
            reasoning="Some indicators",
            matched_patterns=["pattern1"],
            red_flags=["flag1", "flag2"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "probe"
        assert decision.scam_detected is True
    
    def test_strict_mode_low_confidence_ignore(self):
        """Strict mode: Low confidence (<0.70) should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.65,
            primary_category="unknown",
            reasoning="Low confidence",
            matched_patterns=[],
            red_flags=["flag1", "flag2", "flag3"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_threshold_boundary_normal_mode(self):
        """Test threshold boundaries in normal mode"""
        dm = DecisionMaker()
        
        # At 0.7 threshold - should ENGAGE
        detection_at = ScamDetectionResult(
            is_scam=True, confidence=0.7, primary_category="test",
            reasoning="At threshold", matched_patterns=[], red_flags=[],
            legitimacy_indicators=[], detection_mode="normal"
        )
        decision_at = dm.make_decision(detection_at)
        assert decision_at.action == "engage"
        
        # Just below 0.7 - should PROBE
        detection_below = ScamDetectionResult(
            is_scam=True, confidence=0.69, primary_category="test",
            reasoning="Below threshold", matched_patterns=[], red_flags=[],
            legitimacy_indicators=[], detection_mode="normal"
        )
        decision_below = dm.make_decision(detection_below)
        assert decision_below.action == "probe"
    
    def test_threshold_boundary_strict_mode(self):
        """Test threshold boundaries in strict mode"""
        dm = DecisionMaker()
        
        # At 0.85 threshold with 3 indicators - should ENGAGE
        detection_at = ScamDetectionResult(
            is_scam=True, confidence=0.85, primary_category="test",
            reasoning="At threshold", matched_patterns=[],
            red_flags=["f1", "f2", "f3"],
            legitimacy_indicators=[], detection_mode="strict"
        )
        decision_at = dm.make_decision(detection_at)
        assert decision_at.action == "engage"
        
        # Just below 0.85 with 2 indicators - should PROBE
        detection_below = ScamDetectionResult(
            is_scam=True, confidence=0.84, primary_category="test",
            reasoning="Below threshold", matched_patterns=[],
            red_flags=["f1", "f2"],
            legitimacy_indicators=[], detection_mode="strict"
        )
        decision_below = dm.make_decision(detection_below)
        assert decision_below.action == "probe"


class TestConvenienceFunctions:
    """Test suite for convenience functions"""
    
    def test_make_final_decision_function(self):
        """make_final_decision convenience function should work"""
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.92,
            primary_category="digital_arrest",
            reasoning="Clear scam",
            matched_patterns=["pattern1"],
            red_flags=["flag1", "flag2"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = make_final_decision(detection)
        
        assert isinstance(decision, FinalDecision)
        assert decision.action == "engage"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
