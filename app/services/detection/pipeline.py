"""
Detection Pipeline Orchestrator (Phase 2 - Complete)

Coordintates all detection steps:
1. Pre-Screening (Phase 2.1)
2. Language Detection (Phase 2.2)
3. Language Routing (Phase 2.3)
4. RAG + LLM Detection (Phase 2.4A/B)
5. Decision Making (Phase 2.4)
6. Session Update (Phase 2.5)
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.models.schemas import MessageRequest, MessageResponse
from app.models.session import SessionData
from app.services.session.manager import get_session_manager

# Phase 2 Components
from app.services.detection.pre_screen import pre_screen_message
from app.services.detection.language_detector import detect_and_route
from app.services.detection.rag_retriever import retrieve_rag_evidence
from app.services.detection.llm_detector import detect_scam_normal_mode, detect_scam_strict_mode
from app.services.detection.decision_maker import make_final_decision, FinalDecision


class DetectionPipeline:
    """
    Orchestrates the scam detection workflow.
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
        
        print(f"\n--- Starting Detection Pipeline for Session: {session_id} ---")
        print(f"Incoming Message: {message_text[:50]}...")
        
        # ----------------------------------------------------
        # Step 2.1: Pre-Screening
        # ----------------------------------------------------
        screen_result = pre_screen_message(request)
        if hasattr(screen_result, 'passed'):  # Handle different return types if any
             if not screen_result.passed:
                print(f"[REJECT] Pre-screening rejected: {screen_result.reason}")
                return {"action": "ignore", "reason": screen_result.reason}
        elif hasattr(screen_result, 'action') and screen_result.action == "ignore":
             # Support alternative result structure just in case
             print(f"[REJECT] Pre-screening rejected: {getattr(screen_result, 'reason', 'unknown')}")
             return {"action": "ignore", "reason": getattr(screen_result, 'reason', 'unknown')}
        
        # ----------------------------------------------------
        # Step 2.2 & 2.3: Language Detection & Routing
        # ----------------------------------------------------
        lang_result = detect_and_route(message_text)
        print(f"[LANG] Detected Language: {lang_result.language} (Confidence: {lang_result.confidence:.2f})")
        print(f"[ROUTE] Routing to: {lang_result.mode.upper()} MODE")
        
        # ----------------------------------------------------
        # Step 2.4: Detection (RAG + LLM)
        # ----------------------------------------------------
        if lang_result.mode == "normal":
            # Phase 2.4A: Normal Mode (RAG + LLM)
            rag_result = retrieve_rag_evidence(message_text)
            print(f"[RAG] Evidence: {len(rag_result.matches)} matches found")
            
            detection_result = detect_scam_normal_mode(
                message_text, rag_result, lang_result.language
            )
        else:
            # Phase 2.4B: Strict Mode (LLM-only)
            print("[INFO] Skipping RAG for Strict Mode")
            detection_result = detect_scam_strict_mode(
                message_text, lang_result.language
            )
            
        print(f"[LLM] Judgment: is_scam={detection_result.is_scam}, conf={detection_result.confidence:.2f}")
        
        # ----------------------------------------------------
        # Step 2.4 (Part 2): Decision Making
        # ----------------------------------------------------
        final_decision = make_final_decision(detection_result)
        print(f"[DECISION] Final Decision: {final_decision.action.upper()}")
        
        # ----------------------------------------------------
        # Step 2.5: Update Session & Store Metadata
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
        Update session with detection results (Phase 2.5).
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
            session.detection_mode = decision.detection_mode
            session.detected_language = lang_result.language
            session.language_confidence = lang_result.confidence
            
            session.category = decision.category
            session.confidence = decision.confidence
            session.reasoning = decision.reasoning
            session.red_flags = decision.red_flags
            
            print("[SESSION] Session updated with scam indicators")
        
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
