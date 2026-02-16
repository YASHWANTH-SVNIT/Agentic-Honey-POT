"""
Adaptive Engagement Agent - Orchestrates dynamic, intelligent conversation flow
Uses content-based states, goal-oriented extraction, and natural responses
"""
from typing import Dict, Any, List, Optional
from app.models.session import SessionData
from app.services.engagement.persona_selector import DynamicPersonaGenerator
from app.services.engagement.stage_manager import ConversationStateAnalyzer
from app.services.engagement.prompt_builder import AdaptivePromptBuilder
from app.services.engagement.goal_tracker import ExtractionGoalTracker
from app.services.engagement.scammer_analyzer import ScammerBehaviorAnalyzer
from app.services.engagement.stop_checker import StopConditionChecker
from app.services.intelligence.investigator import InvestigatorAgent
from app.services.llm.client import get_llm_client
from app.services.finalization.guvi_callback import GUVICallbackClient
import settings


class EngagementAgent:
    """
    Adaptive Engagement Agent with:
    - Dynamic persona generation (no static JSON)
    - Content-based state detection (not turn-based)
    - Goal-oriented extraction
    - Natural response length (no word limits)
    - Scammer behavior adaptation
    """
    
    @classmethod
    async def generate_response(cls, session: SessionData, message_text: str, history: List[Dict[str, str]]) -> str:
        """
        Main orchestration method for Phase 3 Engagement.
        
        Flow:
        1. Extract intelligence from scammer's message
        2. Analyze scammer's behavior (tone, urgency)
        3. Determine conversation state (content-based)
        4. Get next extraction goal
        5. Generate adaptive persona
        6. Build intelligent prompt
        7. Generate natural response
        8. Handle completion/reporting
        """
        
        print(f"\n{'='*50}")
        print(f"[Agent] Turn {session.turn_count + 1} - Processing message...")
        print(f"{'='*50}")
        
        # ============================================
        # 1. AI-POWERED INTELLIGENCE EXTRACTION
        # ============================================
        print(f"[Agent] Extracting intelligence...")
        try:
            investigator_result = await InvestigatorAgent.analyze(
                text=message_text,
                conversation_history=history
            )
            
            new_intel = investigator_result.get("intelligence", {})
            intel_count = sum(len(v) if isinstance(v, list) else 1 for v in new_intel.values() if v)
            print(f"[Agent] Extracted {intel_count} new items")
            
            if new_intel:
                session.extracted_intel = InvestigatorAgent.merge_intelligence(
                    existing=session.extracted_intel,
                    new=new_intel
                )
        except Exception as e:
            print(f"[Agent] Extraction error: {e}")
        
        # ============================================
        # 2. ANALYZE SCAMMER BEHAVIOR
        # ============================================
        scammer_tone = ScammerBehaviorAnalyzer.analyze_tone(message_text)
        is_urgent = ScammerBehaviorAnalyzer.detect_urgency(message_text)
        has_threat = ScammerBehaviorAnalyzer.detect_threat(message_text)
        payment_info = ScammerBehaviorAnalyzer.detect_payment_info_given(message_text)
        
        print(f"[Agent] Scammer tone: {scammer_tone}, Urgent: {is_urgent}, Threat: {has_threat}")
        print(f"[Agent] Payment info in message: {payment_info}")
        
        # ============================================
        # 3. UPDATE TURN COUNT
        # ============================================
        session.turn_count += 1
        
        # Ensure category exists
        if not session.category:
            session.category = "default"
        
        # ============================================
        # 4. DETERMINE CONVERSATION STATE (CONTENT-BASED)
        # ============================================
        conversation_state = ConversationStateAnalyzer.determine_state(
            history=history,
            extracted_intel=session.extracted_intel,
            turn_count=session.turn_count,
            scammer_tone=scammer_tone
        )
        session.stage = conversation_state  # Update session with current state
        
        print(f"[Agent] Conversation state: {conversation_state}")
        
        # ============================================
        # 5. GET EXTRACTION GOAL
        # ============================================
        extraction_progress = ExtractionGoalTracker.get_extraction_progress(
            extracted=session.extracted_intel,
            category=session.category
        )
        next_goal = extraction_progress.get("next_goal")
        
        print(f"[Agent] Extraction progress: {extraction_progress['percentage']:.0f}%")
        print(f"[Agent] Next goal: {next_goal}")
        
        # ============================================
        # 6. GENERATE ADAPTIVE PERSONA
        # ============================================
        persona_traits = DynamicPersonaGenerator.generate_adaptive_persona(
            scam_category=session.category,
            turn_count=session.turn_count,
            scammer_tone=scammer_tone,
            extracted_intel=session.extracted_intel
        )
        
        # Store persona name in session for tracking
        session.persona = persona_traits.get("character_summary", "Adaptive Persona")
        
        print(f"[Agent] Persona: {persona_traits.get('primary_emotion')} / {persona_traits.get('compliance_style', '')[:30]}")
        
        # ============================================
        # 7. CHECK STOP CONDITIONS
        # ============================================
        should_stop = StopConditionChecker.should_stop(session)
        if should_stop or session.turn_count >= settings.MAX_TURNS:
            conversation_state = "exhaustion_stalling"
            session.stage = "termination"
            print(f"[Agent] Stop condition triggered - entering termination")
        
        # ============================================
        # 8. BUILD INTELLIGENT PROMPT
        # ============================================
        prompt = AdaptivePromptBuilder.create_prompt(
            session=session,
            latest_message=message_text,
            history=history
        )
        
        # ============================================
        # 9. GENERATE RESPONSE (Natural Length)
        # ============================================
        llm_client = get_llm_client()
        reply_text = ""
        
        try:
            # Higher max_tokens for natural length, moderate temperature for creativity + coherence
            # NOTE: Timeout is 25s to leave 5s buffer for GUVI's 30s max requirement
            response = llm_client.generate(
                prompt, 
                temperature=0.7,  # Balanced creativity
                max_tokens=150,   # Allow longer natural responses
                timeout=25.0      # 25s timeout (GUVI requires <30s response)
            )
            
            # Clean up response
            reply_text = response.strip()
            
            # Remove any quote marks
            reply_text = reply_text.replace('"', '').replace("'", "'")
            
            # Remove any "Response:" or similar prefixes
            prefixes_to_remove = ["response:", "reply:", "you:", "agent:", "me:"]
            reply_lower = reply_text.lower()
            for prefix in prefixes_to_remove:
                if reply_lower.startswith(prefix):
                    reply_text = reply_text[len(prefix):].strip()
                    break
            
            # Soft limit: if extremely long, truncate gracefully
            word_count = len(reply_text.split())
            if word_count > 50:
                # Find a natural break point
                sentences = reply_text.split('.')
                truncated = []
                current_words = 0
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if current_words + sentence_words <= 40:
                        truncated.append(sentence)
                        current_words += sentence_words
                    else:
                        break
                if truncated:
                    reply_text = '.'.join(truncated) + '.'
                else:
                    reply_text = ' '.join(reply_text.split()[:35]) + '...'
                print(f"[Agent] Response trimmed from {word_count} to {len(reply_text.split())} words")
            
            print(f"[Agent] Generated reply ({len(reply_text.split())} words): {reply_text[:80]}...")
            
        except Exception as e:
            print(f"[Agent] Generation Error: {e}")
            # Context-aware fallback based on scammer tone
            if scammer_tone == "aggressive":
                reply_text = "ok ok im trying plz wait"
            elif has_threat:
                reply_text = "im scared what do i do"
            else:
                reply_text = "umm wait let me understand"
        
        # ============================================
        # 10. CHECK FOR COMPLETION & REPORT TO GUVI
        # ============================================
        if session.stage == "termination" or should_stop:
            if not getattr(session, "reported_to_guvi", False):
                print(f"[Agent] Conversation ending. Reporting to GUVI...")
                
                notes = f"Category: {session.category}. "
                notes += f"Turns: {session.turn_count}. "
                notes += f"Extraction: {extraction_progress['percentage']:.0f}%. "
                notes += f"Reason: {session.reasoning or 'Max turns reached'}"
                
                try:
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
                        print(f"[Agent] Successfully reported to GUVI")
                except Exception as e:
                    print(f"[Agent] GUVI reporting error: {e}")
        
        print(f"[Agent] Turn {session.turn_count} complete\n")
        
        return reply_text