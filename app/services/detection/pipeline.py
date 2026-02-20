"""
Detection Pipeline Orchestrator (Phase 2 - Simplified)

Coordinates all detection steps:
1. Pre-Screening
2. RAG + LLM Detection
3. Decision Making (engage/probe/ignore)
4. Session Update

Changes:
- REMOVED: Language detection (unnecessary barrier)
- SIMPLIFIED: Single detection path
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.models.schemas import MessageRequest
from app.models.session import SessionData
from app.services.session.manager import get_session_manager

# Phase 2 Components
from app.services.detection.pre_screen import pre_screen_message
from app.services.detection.rag_retriever import retrieve_rag_evidence
from app.services.detection.llm_detector import detect_scam_normal_mode
from app.services.detection.decision_maker import make_final_decision, FinalDecision


class DetectionPipeline:
    """
    Orchestrates the scam detection workflow (SIMPLIFIED VERSION).
    No language detection - accepts all messages.
    """

    def __init__(self):
        """Initialize pipeline"""
        self.session_manager = get_session_manager()

    async def process(self, request: MessageRequest) -> Dict[str, Any]:
        """
        Process an incoming message through the detection pipeline.

        Args:
            request: Incoming message request

        Returns:
            Dict containing pipeline results and action
        """
        message_text = request.message.text
        session_id = request.sessionId

        # Get or create session
        session = self.session_manager.get_session(session_id)
        if not session:
            session = self.session_manager.create_session(session_id)

        print(f"\n--- Detection Pipeline: {session_id} ---")
        print(f"Message: {message_text[:50]}...")

        # ----------------------------------------------------
        # Step 1: Pre-Screening (Null/Empty checks)
        # ----------------------------------------------------
        screen_result = pre_screen_message(request)
        if not screen_result.passed:
            print(f"[Pipeline] Pre-screening rejected: {screen_result.reason}")
            return {"action": "ignore", "reason": screen_result.reason}

        # ----------------------------------------------------
        # Step 2: RAG + LLM Detection
        # ----------------------------------------------------
        # Retrieve RAG evidence
        rag_result = retrieve_rag_evidence(message_text)
        print(f"[Pipeline] RAG: {len(rag_result.matches)} matches found")

        # Run LLM detection with RAG context (language defaulted to 'en')
        detection_result = detect_scam_normal_mode(
            message_text, rag_result, "en"
        )

        print(f"[Pipeline] LLM: is_scam={detection_result.is_scam}, conf={detection_result.confidence:.2f}")

        # ----------------------------------------------------
        # Step 3: Decision Making
        # ----------------------------------------------------
        final_decision = make_final_decision(detection_result)
        print(f"[Pipeline] Decision: {final_decision.action.upper()}")

        # ----------------------------------------------------
        # Step 4: Update Session
        # ----------------------------------------------------
        await self._update_session_with_decision(
            session,
            final_decision,
            message_text
        )

        # ----------------------------------------------------
        # Return Result
        # ----------------------------------------------------
        if final_decision.action == "ignore":
            return {"action": "ignore", "decision": final_decision}

        # If ENGAGE or PROBE, main loop will trigger engagement phase
        return {
            "action": final_decision.action,
            "decision": final_decision,
            "session_id": session_id
        }

    async def _update_session_with_decision(
        self,
        session: SessionData,
        decision: FinalDecision,
        message_text: str
    ):
        """
        Update session with detection results.
        """
        # Add message to history
        session.conversation_history.append({
            "role": "user",
            "content": message_text,
            "timestamp": datetime.now().isoformat()
        })
        session.turn_count += 1

        if decision.action in ["engage", "probe"]:
            # Valid detection - update session metadata
            session.scam_detected = True
            session.stage = "engagement"
            session.updated_at = datetime.now()

            # Store metadata
            session.detected_language = "en"
            session.language_confidence = 1.0

            session.category = decision.category
            session.confidence = decision.confidence
            session.reasoning = decision.reasoning
            session.red_flags = decision.red_flags

            print("[Pipeline] Session updated with scam indicators")

        # Save session
        self.session_manager.update_session(session)


# ============================================================
# Global Singleton Instance
# ============================================================

_pipeline: Optional[DetectionPipeline] = None


def get_detection_pipeline() -> DetectionPipeline:
    """Get or create global pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = DetectionPipeline()
    return _pipeline


async def run_detection_pipeline(request: MessageRequest) -> Dict[str, Any]:
    """Convenience function to run pipeline"""
    pipeline = get_detection_pipeline()
    return await pipeline.process(request)
