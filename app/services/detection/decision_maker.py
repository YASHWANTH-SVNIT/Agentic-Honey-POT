"""
Decision Maker for Scam Detection (Phase 2.4 - Final Step)

This module applies confidence thresholds to LLM detection results
and makes the final decision: ENGAGE, PROBE, or IGNORE.

According to README:
- Normal Mode: Threshold 0.7 for ENGAGE, 0.5-0.7 for PROBE
- Strict Mode: Threshold 0.85 for ENGAGE, 0.70-0.85 for PROBE
"""

from typing import Literal
from dataclasses import dataclass
from app.services.detection.llm_detector import ScamDetectionResult
import settings


# Type alias for decision actions
DecisionAction = Literal["engage", "probe", "ignore"]


@dataclass
class FinalDecision:
    """
    Final decision after applying thresholds.
    
    Attributes:
        action: Decision action ('engage', 'probe', or 'ignore')
        scam_detected: Whether scam was detected
        confidence: Confidence score from LLM
        category: Detected scam category
        reasoning: Decision reasoning
        detection_mode: 'normal' or 'strict'
        threshold_used: Threshold that was applied
        red_flags: List of red flags
    """
    action: DecisionAction
    scam_detected: bool
    confidence: float
    category: str | None
    reasoning: str
    detection_mode: str
    threshold_used: float
    red_flags: list


class DecisionMaker:
    """
    Makes final decision based on LLM detection result and confidence thresholds.
    """
    
    def __init__(
        self,
        normal_engage_threshold: float = None,
        normal_probe_threshold: float = None,
        strict_engage_threshold: float = None,
        strict_probe_threshold: float = None
    ):
        """
        Initialize decision maker with thresholds.
        
        Args:
            normal_engage_threshold: Threshold for ENGAGE in normal mode (default from settings)
            normal_probe_threshold: Threshold for PROBE in normal mode (default from settings)
            strict_engage_threshold: Threshold for ENGAGE in strict mode (default from settings)
            strict_probe_threshold: Threshold for PROBE in strict mode (default 0.70)
        """
        # Normal mode thresholds (for EN/HI)
        self.normal_engage_threshold = normal_engage_threshold or settings.NORMAL_MODE_THRESHOLD  # 0.7
        self.normal_probe_threshold = normal_probe_threshold or settings.PROBE_THRESHOLD_MIN  # 0.5
        
        # Strict mode thresholds (for other languages)
        self.strict_engage_threshold = strict_engage_threshold or settings.STRICT_MODE_THRESHOLD  # 0.85
        self.strict_probe_threshold = strict_probe_threshold or 0.70
    
    def make_decision(self, detection_result: ScamDetectionResult) -> FinalDecision:
        """
        Make final decision based on detection result.
        
        Args:
            detection_result: ScamDetectionResult from LLM detector
            
        Returns:
            FinalDecision with action and metadata
        """
        if detection_result.detection_mode == "normal":
            return self._decide_normal_mode(detection_result)
        else:
            return self._decide_strict_mode(detection_result)
    
    def _decide_normal_mode(self, result: ScamDetectionResult) -> FinalDecision:
        """
        Apply Normal Mode decision rules (Phase 2.4A).
        
        According to README Step 2.4A Sub-step 4:
        
        IF is_scam=true AND confidence ≥ 0.7:
            → ENGAGE (high confidence scam)
        
        IF is_scam=true AND confidence 0.5-0.7:
            → PROBE (medium confidence, cautious engagement)
        
        IF is_scam=false OR confidence < 0.5:
            → IGNORE (not a scam or too uncertain)
        """
        if not result.is_scam:
            return FinalDecision(
                action="ignore",
                scam_detected=False,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"LLM classified as NOT scam. {result.reasoning}",
                detection_mode="normal",
                threshold_used=self.normal_engage_threshold,
                red_flags=result.red_flags
            )
        
        # is_scam = True
        if result.confidence >= self.normal_engage_threshold:
            # High confidence scam
            return FinalDecision(
                action="engage",
                scam_detected=True,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"High confidence scam detected. {result.reasoning}",
                detection_mode="normal",
                threshold_used=self.normal_engage_threshold,
                red_flags=result.red_flags
            )
        
        elif result.confidence >= self.normal_probe_threshold:
            # Medium confidence - cautious engagement
            return FinalDecision(
                action="probe",
                scam_detected=True,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"Medium confidence scam. Cautious engagement. {result.reasoning}",
                detection_mode="normal",
                threshold_used=self.normal_probe_threshold,
                red_flags=result.red_flags
            )
        
        else:
            # Low confidence - ignore
            return FinalDecision(
                action="ignore",
                scam_detected=False,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"Confidence too low ({result.confidence:.2f} < {self.normal_probe_threshold}). {result.reasoning}",
                detection_mode="normal",
                threshold_used=self.normal_probe_threshold,
                red_flags=result.red_flags
            )
    
    def _decide_strict_mode(self, result: ScamDetectionResult) -> FinalDecision:
        """
        Apply Strict Mode decision rules (Phase 2.4B).
        
        According to README Step 2.4B:
        
        IF is_scam=true AND confidence ≥ 0.85:
            → ENGAGE (higher threshold: 0.85 vs 0.7)
        
        IF is_scam=true AND confidence 0.70-0.85:
            → PROBE (cautious middle ground)
        
        IF is_scam=true AND confidence < 0.70:
            → IGNORE (prefer safety over engagement)
        
        Additional: Require 3+ malicious indicators to engage
        """
        if not result.is_scam:
            return FinalDecision(
                action="ignore",
                scam_detected=False,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"LLM classified as NOT scam (strict mode). {result.reasoning}",
                detection_mode="strict",
                threshold_used=self.strict_engage_threshold,
                red_flags=result.red_flags
            )
        
        # Check for 3+ malicious indicators (red flags)
        num_indicators = len(result.red_flags)
        
        # is_scam = True
        if result.confidence >= self.strict_engage_threshold and num_indicators >= 3:
            # High confidence scam with sufficient indicators
            return FinalDecision(
                action="engage",
                scam_detected=True,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"High confidence scam with {num_indicators} indicators (strict mode). {result.reasoning}",
                detection_mode="strict",
                threshold_used=self.strict_engage_threshold,
                red_flags=result.red_flags
            )
        
        elif result.confidence >= self.strict_probe_threshold:
            # Medium confidence - cautious engagement
            if num_indicators >= 2:
                return FinalDecision(
                    action="probe",
                    scam_detected=True,
                    confidence=result.confidence,
                    category=result.primary_category,
                    reasoning=f"Medium confidence with {num_indicators} indicators (strict mode). {result.reasoning}",
                    detection_mode="strict",
                    threshold_used=self.strict_probe_threshold,
                    red_flags=result.red_flags
                )
            else:
                # Not enough indicators
                return FinalDecision(
                    action="ignore",
                    scam_detected=False,
                    confidence=result.confidence,
                    category=result.primary_category,
                    reasoning=f"Insufficient indicators ({num_indicators} < 2) despite medium confidence (strict mode).",
                    detection_mode="strict",
                    threshold_used=self.strict_probe_threshold,
                    red_flags=result.red_flags
                )
        
        else:
            # Low confidence - ignore
            return FinalDecision(
                action="ignore",
                scam_detected=False,
                confidence=result.confidence,
                category=result.primary_category,
                reasoning=f"Confidence too low ({result.confidence:.2f} < {self.strict_probe_threshold}) in strict mode. {result.reasoning}",
                detection_mode="strict",
                threshold_used=self.strict_probe_threshold,
                red_flags=result.red_flags
            )


# ============================================================
# Global Singleton Instance
# ============================================================

_decision_maker: DecisionMaker | None = None


def get_decision_maker() -> DecisionMaker:
    """
    Get or create global decision maker instance.
    
    Returns:
        DecisionMaker: Singleton instance
    """
    global _decision_maker
    if _decision_maker is None:
        _decision_maker = DecisionMaker()
    return _decision_maker


# ============================================================
# Convenience Functions
# ============================================================

def make_final_decision(detection_result: ScamDetectionResult) -> FinalDecision:
    """
    Convenience function to make final decision.
    
    Args:
        detection_result: ScamDetectionResult from LLM detector
        
    Returns:
        FinalDecision with action
    """
    decision_maker = get_decision_maker()
    return decision_maker.make_decision(detection_result)
