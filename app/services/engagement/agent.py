from typing import Dict, Any, List, Optional
from app.models.session import SessionData
from app.services.engagement.persona_selector import PersonaSelector
from app.services.engagement.stage_manager import StageManager
from app.services.engagement.prompt_builder import PromptBuilder
from app.services.engagement.stop_checker import StopConditionChecker
from app.services.intelligence.investigator import InvestigatorAgent
from app.services.llm.client import get_llm_client
from app.services.finalization.guvi_callback import GUVICallbackClient
from config.extraction_targets import get_targets_for_category

class EngagementAgent:
    """
    Orchestrates the engagement phase with:
    - AI-powered intelligence extraction (no regex)
    - Casual, varied responses
    - Anti-repetition system
    """
    
    @classmethod
    async def generate_response(cls, session: SessionData, message_text: str, history: List[Dict[str, str]]) -> str:
        """
        Orchestrates the Phase 3 Engagement Logic:
        1. Extract passive intel using AI investigator
        2. Update stage
        3. Select persona
        4. Generate LLM response (casual, varied)
        5. Check for completion and report to GUVI
        """
        
        # ============================================
        # 1. AI-POWERED INTELLIGENCE EXTRACTION
        # ============================================
        print(f"[Agent] Calling AI Investigator for extraction...")
        investigator_result = await InvestigatorAgent.analyze(
            text=message_text,
            conversation_history=history
        )
        
        new_intel = investigator_result.get("intelligence", {})
        print(f"[Agent] Extracted: {sum(len(v) for v in new_intel.values())} items")
        
        if new_intel:
            # Merge into session intel using AI's merge function
            session.extracted_intel = InvestigatorAgent.merge_intelligence(
                existing=session.extracted_intel,
                new=new_intel
            )
        
        # ============================================
        # 2. UPDATE FLOW STATE
        # ============================================
        session.turn_count += 1
        
        # Phase 6 Implementation: Check Stop Conditions
        should_stop = StopConditionChecker.should_stop(session)
        if should_stop:
            session.stage = "termination"
        else:
            session.stage = StageManager.determine_stage(session.turn_count)
             
        stage_config = StageManager.get_stage_config(session.stage)
        
        # ============================================
        # 3. ENSURE PERSONA
        # ============================================
        if not session.category:
            session.category = "default"
        
        persona = PersonaSelector.select_persona(session.category)
        session.persona = persona.get("name") 
        
        # ============================================
        # 4. DETERMINE MISSING TARGETS
        # ============================================
        all_targets = get_targets_for_category(session.category)
        missing_targets = [t for t in all_targets if t not in session.extracted_intel]
        
        # ============================================
        # 5. BUILD PROMPT (with casual language)
        # ============================================
        prompt = PromptBuilder.create_prompt(
            persona=persona,
            category=session.category,
            stage=session.stage,
            stage_config=stage_config,
            turn_count=session.turn_count,
            extracted_intel=session.extracted_intel,
            missing_targets=missing_targets,
            history=history,
            current_message_text=message_text
        )
        
        # ============================================
        # 6. CALL LLM (with LOWER temp and STRICT token limit)
        # ============================================
        llm_client = get_llm_client()
        reply_text = ""
        try:
            # LOWER temperature + STRICT max_tokens for SHORT responses
            response = llm_client.generate(prompt, temperature=0.6, max_tokens=80)
            reply_text = response.strip().replace('"', '')
            
            # SAFETY: Truncate if still too long (should not happen)
            word_count = len(reply_text.split())
            if word_count > 25:
                # Force truncate to 20 words
                words = reply_text.split()[:20]
                reply_text = " ".join(words) + "..."
                print(f"[Agent] WARNING: Response truncated from {word_count} to 20 words")
            
            print(f"[Agent] Generated reply ({len(reply_text.split())} words): {reply_text[:60]}...")
            
        except Exception as e:
            print(f"[Agent] Generation Error: {e}")
            # Fallback to simple confused response
            reply_text = "umm wait im confused"
            
        # ============================================
        # 7. CHECK FOR COMPLETION & REPORT
        # ============================================
        if (session.stage == "termination" and session.turn_count >= 13) or should_stop:
            # Only report once
            if not getattr(session, "reported_to_guvi", False):
                print(f"[Agent] Conversation ending (Turn {session.turn_count}). Reporting to GUVI...")
                 
                notes = f"Category: {session.category}. Reason: {session.reasoning or 'N/A'}"
                 
                success = await GUVICallbackClient.send_final_result(
                    session_id=session.session_id,
                    scam_detected=session.scam_detected,
                    message_count=session.turn_count * 2,
                    intel=session.extracted_intel,
                    red_flags=session.red_flags,
                    notes=notes
                )
                 
                if success:
                    session.reported_to_guvi = True
        
        return reply_text