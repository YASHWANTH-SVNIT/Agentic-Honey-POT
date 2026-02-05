"""
Decision Maker for Scam Detection (Simplified - No Strict Mode)

This module applies confidence thresholds to LLM detection results
and makes the final decision: ENGAGE, PROBE, or IGNORE.
"""

from typing import Literal
from dataclasses import dataclass
from app.services.detection.llm_detector import ScamDetectionResult
import settings


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
        threshold_used: Threshold that was applied
        red_flags: List of red flags
    """
    action: DecisionAction
    scam_detected: bool
    confidence: float
    category: str | None
    reasoning: str
    threshold_used: float
    red_flags: list


class DecisionMaker:
    """
    Makes final decision based on LLM detection result and confidence thresholds.
    
    SIMPLIFIED VERSION - No strict mode, single threshold system.
    """
    
    def __init__(
        self,
        engage_threshold: float = None,
        probe_threshold: float = None
    ):
        """
        Initialize decision maker with thresholds.
        
        Args:
            engage_threshold: Threshold for ENGAGE (default: 0.75)
            probe_threshold: Threshold for PROBE (default: 0.55)
        """
        # Load thresholds from settings
        self.engage_threshold = engage_threshold or getattr(settings, 'DETECTION_THRESHOLD', 0.75)
        self.probe_threshold = probe_threshold or getattr(settings, 'PROBE_THRESHOLD', 0.55)
        
        print(f"[DecisionMaker] Initialized - Engage: {self.engage_threshold}, Probe: {self.probe_threshold}")
        
    def make_decision(self, detection_result: ScamDetectionResult) -> FinalDecision:
        """
        Make final decision based on detection result.
        
        Rules (SIMPLIFIED):
        IF is_scam=true AND confidence >= 0.75 → ENGAGE (high confidence scam)
        IF is_scam=true AND confidence >= 0.55 → PROBE (medium confidence)
        ELSE → IGNORE
            
        Args:
            detection_result: ScamDetectionResult from LLM detector
            
        Returns:
            FinalDecision with action and metadata
        """
        if not detection_result.is_scam:
            return FinalDecision(
                action="ignore",
                scam_detected=False,
                confidence=detection_result.confidence,
                category=detection_result.primary_category,
                reasoning=f"LLM classified as NOT scam. {detection_result.reasoning}",
                threshold_used=self.engage_threshold,
                red_flags=detection_result.red_flags
            )
        
        # is_scam = True
        if detection_result.confidence >= self.engage_threshold:
            # High confidence scam → ENGAGE fully
            return FinalDecision(
                action="engage",
                scam_detected=True,
                confidence=detection_result.confidence,
                category=detection_result.primary_category,
                reasoning=f"High confidence scam detected. {detection_result.reasoning}",
                threshold_used=self.engage_threshold,
                red_flags=detection_result.red_flags
            )
        
        elif detection_result.confidence >= self.probe_threshold:
            # Medium confidence → PROBE (cautious engagement)
            return FinalDecision(
                action="probe",
                scam_detected=True,
                confidence=detection_result.confidence,
                category=detection_result.primary_category,
                reasoning=f"Medium confidence scam. Cautious engagement. {detection_result.reasoning}",
                threshold_used=self.probe_threshold,
                red_flags=detection_result.red_flags
            )
        
        else:
            # Low confidence → IGNORE
            return FinalDecision(
                action="ignore",
                scam_detected=False,
                confidence=detection_result.confidence,
                category=detection_result.primary_category,
                reasoning=f"Confidence too low ({detection_result.confidence:.2f} < {self.probe_threshold}). {detection_result.reasoning}",
                threshold_used=self.probe_threshold,
                red_flags=detection_result.red_flags
            )


# ============================================================
# Global Singleton Instance
# ============================================================

_decision_maker: DecisionMaker | None = None


def get_decision_maker() -> DecisionMaker:
    """Get or create global decision maker instance."""
    global _decision_maker
    if _decision_maker is None:
        _decision_maker = DecisionMaker()
    return _decision_maker


def make_final_decision(detection_result: ScamDetectionResult) -> FinalDecision:
    """Convenience function to make final decision."""
    decision_maker = get_decision_maker()
    return decision_maker.make_decision(detection_result)
