"""
Unit tests for Phase 2.4: Decision Making Logic

Tests decision maker logic without requiring full LLM/RAG stack.
"""

import pytest
from app.services.detection.llm_detector import ScamDetectionResult
from app.services.detection.decision_maker import (
    DecisionMaker,
    FinalDecision,
    make_final_decision
)


class TestDecisionMakerLogic:
    """Test suite for Decision Maker logic"""
    
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


class TestNormalModeDecisions:
    """Test Normal Mode decision logic (Phase 2.4A)"""
    
    def test_high_confidence_engage(self):
        """Normal mode: High confidence (≥0.7) should ENGAGE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.92,
            primary_category="digital_arrest",
            reasoning="Clear scam indicators detected",
            matched_patterns=["authority_impersonation"],
            red_flags=["Personal phone", "Urgency", "Threats"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "engage"
        assert decision.scam_detected is True
        assert decision.confidence == 0.92
        assert decision.category == "digital_arrest"
        assert decision.detection_mode == "normal"
    
    def test_medium_confidence_probe(self):
        """Normal mode: Medium confidence (0.5-0.7) should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.6,
            primary_category="job_fraud",
            reasoning="Some scam indicators present",
            matched_patterns=["fake_job_posting"],
            red_flags=["Registration fee"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "probe"
        assert decision.scam_detected is True
        assert decision.confidence == 0.6
    
    def test_low_confidence_ignore(self):
        """Normal mode: Low confidence (<0.5) should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.4,
            primary_category="unknown",
            reasoning="Uncertain classification",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_not_scam_ignore(self):
        """Normal mode: is_scam=False should IGNORE regardless of confidence"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=False,
            confidence=0.95,
            primary_category=None,
            reasoning="Legitimate message with official indicators",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=["Official domain", "Transaction ID"],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_threshold_boundary_at_0_7(self):
        """Normal mode: Exactly 0.7 should ENGAGE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.7,
            primary_category="kyc_banking",
            reasoning="At threshold",
            matched_patterns=["fake_kyc"],
            red_flags=["Suspicious URL"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        assert decision.action == "engage"
    
    def test_threshold_boundary_below_0_7(self):
        """Normal mode: Just below 0.7 should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.69,
            primary_category="kyc_banking",
            reasoning="Just below threshold",
            matched_patterns=["fake_kyc"],
            red_flags=["Suspicious URL"],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        assert decision.action == "probe"
    
    def test_threshold_boundary_at_0_5(self):
        """Normal mode: Exactly 0.5 should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.5,
            primary_category="unknown",
            reasoning="At probe threshold",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        assert decision.action == "probe"
    
    def test_threshold_boundary_below_0_5(self):
        """Normal mode: Just below 0.5 should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.49,
            primary_category="unknown",
            reasoning="Below probe threshold",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=[],
            detection_mode="normal"
        )
        
        decision = dm.make_decision(detection)
        assert decision.action == "ignore"


class TestStrictModeDecisions:
    """Test Strict Mode decision logic (Phase 2.4B)"""
    
    def test_high_confidence_with_sufficient_indicators_engage(self):
        """Strict mode: High confidence (≥0.85) + 3+ indicators should ENGAGE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.90,
            primary_category="digital_arrest",
            reasoning="Multiple clear scam indicators",
            matched_patterns=["authority_impersonation", "payment_demand"],
            red_flags=["Threat", "Urgency", "Payment demand", "Fake authority"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "engage"
        assert decision.scam_detected is True
        assert decision.detection_mode == "strict"
        assert "4 indicators" in decision.reasoning
    
    def test_high_confidence_insufficient_indicators_ignore(self):
        """Strict mode: High confidence but <3 indicators should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.90,
            primary_category="unknown",
            reasoning="High confidence but few clear indicators",
            matched_patterns=[],
            red_flags=["flag1", "flag2"],  # Only 2 indicators
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
        assert "Insufficient indicators" in decision.reasoning
    
    def test_medium_confidence_with_indicators_probe(self):
        """Strict mode: Medium confidence (0.70-0.85) + 2+ indicators should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.75,
            primary_category="job_fraud",
            reasoning="Some indicators present",
            matched_patterns=["fake_job"],
            red_flags=["Registration fee", "Suspicious contact"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "probe"
        assert decision.scam_detected is True
    
    def test_medium_confidence_insufficient_indicators_ignore(self):
        """Strict mode: Medium confidence but <2 indicators should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.75,
            primary_category="unknown",
            reasoning="Medium confidence, few indicators",
            matched_patterns=[],
            red_flags=["single_flag"],  # Only 1 indicator
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_low_confidence_ignore(self):
        """Strict mode: Low confidence (<0.70) should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.65,
            primary_category="unknown",
            reasoning="Low confidence",
            matched_patterns=[],
            red_flags=["flag1", "flag2", "flag3"],  # Even with 3 indicators
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_not_scam_ignore(self):
        """Strict mode: is_scam=False should IGNORE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=False,
            confidence=0.95,
            primary_category=None,
            reasoning="Not classified as scam",
            matched_patterns=[],
            red_flags=[],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        
        assert decision.action == "ignore"
        assert decision.scam_detected is False
    
    def test_threshold_boundary_at_0_85_with_indicators(self):
        """Strict mode: Exactly 0.85 with 3 indicators should ENGAGE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.85,
            primary_category="test",
            reasoning="At threshold",
            matched_patterns=[],
            red_flags=["flag1", "flag2", "flag3"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        assert decision.action == "engage"
    
    def test_threshold_boundary_below_0_85(self):
        """Strict mode: Just below 0.85 with 2 indicators should PROBE"""
        dm = DecisionMaker()
        
        detection = ScamDetectionResult(
            is_scam=True,
            confidence=0.84,
            primary_category="test",
            reasoning="Below engage threshold",
            matched_patterns=[],
            red_flags=["flag1", "flag2"],
            legitimacy_indicators=[],
            detection_mode="strict"
        )
        
        decision = dm.make_decision(detection)
        assert decision.action == "probe"


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_make_final_decision(self):
        """make_final_decision should work correctly"""
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
        assert decision.scam_detected is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
