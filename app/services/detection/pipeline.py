"""
Detection Pipeline Orchestrator (Phase 2 - Simplified)

Coordinates all detection steps:
1. Pre-Screening
2. Language Detection (English only)
3. RAG + LLM Detection (normal mode only)
4. Decision Making (engage/probe/ignore)
5. Session Update

Changes from original:
- REMOVED: Strict mode routing
- SIMPLIFIED: Single detection path
- FIXED: No detection_mode field in session
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.models.schemas import MessageRequest
from app.models.session import SessionData
from app.services.session.manager import get_session_manager

# Phase 2 Components
from app.services.detection.pre_screen import pre_screen_message
from app.services.detection.language_detector import detect_and_route
from app.services.detection.rag_retriever import retrieve_rag_evidence
from app.services.detection.llm_detector import detect_scam_normal_mode
from app.services.detection.decision_maker import make_final_decision, FinalDecision


class DetectionPipeline:
    """
    Orchestrates the scam detection workflow (SIMPLIFIED VERSION).
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
        # Step 2: Language Detection (English only)
        # ----------------------------------------------------
        metadata = request.metadata if hasattr(request, 'metadata') else None
        lang_result = detect_and_route(message_text, metadata)
        print(f"[Pipeline] Language: {lang_result.language} (conf: {lang_result.confidence:.2f})")
        
        # Reject non-English
        if not lang_result.supported:
            print(f"[Pipeline] Language not supported: {lang_result.language}")
            return {
                "action": "not_supported", 
                "reason": f"Language '{lang_result.language}' is not supported. English only."
            }
        
        print(f"[Pipeline] Language supported - proceeding")
        
        # ----------------------------------------------------
        # Step 3: RAG + LLM Detection (Normal mode only)
        # ----------------------------------------------------
        # Retrieve RAG evidence
        rag_result = retrieve_rag_evidence(message_text)
        print(f"[Pipeline] RAG: {len(rag_result.matches)} matches found")
        
        # Run LLM detection with RAG context
        detection_result = detect_scam_normal_mode(
            message_text, rag_result, lang_result.language
        )
            
        print(f"[Pipeline] LLM: is_scam={detection_result.is_scam}, conf={detection_result.confidence:.2f}")
        
        # ----------------------------------------------------
        # Step 4: Decision Making
        # ----------------------------------------------------
        final_decision = make_final_decision(detection_result)
        print(f"[Pipeline] Decision: {final_decision.action.upper()}")
        
        # ----------------------------------------------------
        # Step 5: Update Session
        # ----------------------------------------------------
        await self._update_session_with_decision(
            session, 
            final_decision, 
            lang_result, 
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
        lang_result: Any,
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
            
            # Store metadata (NO detection_mode field)
            session.detected_language = lang_result.language
            session.language_confidence = lang_result.confidence
            
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
