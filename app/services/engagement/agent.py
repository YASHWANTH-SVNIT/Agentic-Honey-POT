from typing import Dict, Any, List, Optional
from app.models.session import SessionData
from app.services.engagement.persona_selector import PersonaSelector
from app.services.engagement.stage_manager import StageManager
from app.services.engagement.prompt_builder import PromptBuilder
from app.services.engagement.stop_checker import StopConditionChecker
from app.services.intelligence.extractors import IntelExtractor
from app.services.llm.client import get_llm_client
from app.services.finalization.guvi_callback import GUVICallbackClient
from config.extraction_targets import get_targets_for_category

class EngagementAgent:
    
    @classmethod
    async def generate_response(cls, session: SessionData, message_text: str, history: List[Dict[str, str]]) -> str:
        """
        Orchestrates the Phase 3 Engagement Logic:
        1. Extract passive intel
        2. Update stage
        3. Select persona
        4. Generate LLM response
        5. Check for completion and report to GUVI
        """
        
        # 1. Passive Intelligence Extraction
        new_intel = IntelExtractor.extract_all(message_text)
        if new_intel:
            # Merge into session intel
            for key, val in new_intel.items():
                if key not in session.extracted_intel:
                    session.extracted_intel[key] = []
                # Add unique values
                if isinstance(session.extracted_intel[key], list):
                    current_vals = set(session.extracted_intel[key])
                    for v in val:
                        current_vals.add(v)
                    session.extracted_intel[key] = list(current_vals)
                else:
                    # Handle case if it wasn't a list for some reason
                    session.extracted_intel[key] = val
        
        # 2. Update Flow State
        session.turn_count += 1
        
        # Phase 6 Implementation: Check Stop Conditions
        should_stop = StopConditionChecker.should_stop(session)
        if should_stop:
            session.stage = "termination"
        else:
             session.stage = StageManager.determine_stage(session.turn_count)
             
        stage_config = StageManager.get_stage_config(session.stage)
        
        # 3. Ensure Persona
        if not session.category:
            session.category = "default"
        
        persona = PersonaSelector.select_persona(session.category)
        session.persona = persona.get("name") 
        
        # 4. Determine Missing Targets
        all_targets = get_targets_for_category(session.category)
        missing_targets = [t for t in all_targets if t not in session.extracted_intel]
        
        # 5. Build Prompt
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
        
        # 6. Call LLM
        # Implementation of dynamic temperature: Starts steady, gets more erratic/emotional as turns increase
        llm_client = get_llm_client()
        
        # Calculate dynamic temperature
        if session.turn_count <= 3:
            temp = 0.7  # Steady and clear
        elif session.stage == "extraction":
            temp = 0.95 # High emotional variance/panic
        else:
            temp = 0.85 # Natural human variance
            
        reply_text = ""
        try:
            response = llm_client.generate(prompt, temperature=temp, max_tokens=150)
            reply_text = response.strip().replace('"', '') # Basic cleanup
        except Exception as e:
            print(f"Agent Generation Error: {e}")
            reply_text = "I'm not sure I understand. Can you explain that again?"
            
        # 7. Check for Completion (Termination Phase or High Turn Count)
        # We report if we are deep in the termination phase or hit a turn limit
        if (session.stage == "termination" and session.turn_count >= 20) or should_stop:
             # Only report once
             if not getattr(session, "reported_to_guvi", False):
                 print(f"[Engagement] Conversation ending (Turn {session.turn_count}). Reporting to GUVI...")
                 
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
