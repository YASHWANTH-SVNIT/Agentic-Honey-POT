"""
Adaptive Prompt Builder - Builds intelligent, context-aware prompts
No word limits - natural response length based on context
Focuses on reacting to actual messages, not generic responses
"""
from typing import Dict, List, Any, Optional
from .scammer_analyzer import ScammerBehaviorAnalyzer
from .goal_tracker import ExtractionGoalTracker
from .stage_manager import ConversationStateAnalyzer
from .persona_selector import DynamicPersonaGenerator
from .anti_detection import AntiDetectionAnalyzer


class AdaptivePromptBuilder:
    """Builds intelligent prompts that adapt to conversation context"""
    
    BASE_TEMPLATE = """You are a REAL PERSON (not AI/bot) being contacted by someone.
REACT NATURALLY to what they just said. Don't be generic.

=== YOUR CHARACTER ===
{character_description}
Current Emotional State: {emotional_state}
Your Reaction Style: {communication_style}

=== WHAT'S HAPPENING ===
Scam Type: {scam_type}
Conversation Phase: {conversation_phase}
Scammer's Behavior: {scammer_behavior}

=== RECENT CONVERSATION ===
{recent_history}

=== WHAT JUST HAPPENED ===
"{latest_message}"
Analysis: {last_exchange_summary}

=== YOUR STRATEGIC GOAL (be subtle!) ===
{extraction_strategy}

=== HOW TO RESPOND ===
1. REACT to what they JUST SAID - don't ignore their message!
2. If they gave payment info (UPI, number, account) → Say "Okay, let me try" or similar
3. If you're "trying" something → Can mention small issues after 1-2 exchanges
4. If you need more info → Ask naturally, don't be obvious about it
5. Match your emotional state - {emotion_hint}
6. Sound human but correct: Use proper grammar and complete sentences. Minimize spelling mistakes. Do not use internet slang (like 'u', 'plz', 'wat').

=== FORBIDDEN (don't use these - too robotic) ===
{forbidden_phrases}

=== RESPOND NOW ===
Write a natural response. Can be short (5 words) or longer (30 words) depending on what makes sense.
Don't use quotation marks. Just write your response directly:"""

    # Emotion-specific hints for the LLM
    EMOTION_HINTS = {
        "terrified": "You're SCARED - short panicked responses, ask worried questions, 'plz dont arrest me'",
        "scared": "You're nervous - worried questions, need reassurance, 'is this real?', 'what should i do?'",
        "excited": "You're EXCITED - happy, eager, 'omg i won??', 'how do i claim it?!', use exclamation marks",
        "hopeful": "You're hopeful - grateful, polite, 'thank you sir', 'when can i start?', eager to cooperate",
        "confused": "You're confused - ask for clarification, 'i dont understand', 'wat?', short confused responses",
        "trusting": "You trust them - warm, caring, 'ok i believe you', willing to help",
        "worried": "You're worried - concerned but trying to help, 'ok let me try', 'what if something goes wrong?'"
    }
    
    @classmethod
    def format_history(cls, history: List[Dict[str, str]], max_messages: int = 6) -> str:
        """Format recent conversation history"""
        if not history:
            return "(This is the start of the conversation)"
        
        # Take last N messages
        recent = history[-max_messages:] if len(history) > max_messages else history
        
        formatted = []
        for msg in recent:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:200]  # Truncate long messages
            
            if role == "user":
                formatted.append(f"THEM: {content}")
            else:
                formatted.append(f"YOU: {content}")
        
        return "\n".join(formatted)
    
    @classmethod
    def create_prompt(
        cls,
        session,
        latest_message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Build an intelligent, context-aware prompt.
        This is the main method that orchestrates all the dynamic components.
        """
        
        # 1. Analyze scammer's behavior
        scammer_tone = ScammerBehaviorAnalyzer.analyze_tone(latest_message)
        last_exchange_summary = ScammerBehaviorAnalyzer.summarize_last_exchange(history, latest_message)
        
        # 2. Determine conversation state (content-based, not turn-based)
        conversation_state = ConversationStateAnalyzer.determine_state(
            history=history,
            extracted_intel=session.extracted_intel,
            turn_count=session.turn_count,
            scammer_tone=scammer_tone
        )
        state_info = ConversationStateAnalyzer.get_state_info(conversation_state)
        
        # 3. Generate adaptive persona traits
        persona_traits = DynamicPersonaGenerator.generate_adaptive_persona(
            scam_category=session.category or "default",
            turn_count=session.turn_count,
            scammer_tone=scammer_tone,
            extracted_intel=session.extracted_intel
        )
        
        # 4. Get extraction strategy
        next_goal = ExtractionGoalTracker.get_next_goal(
            extracted=session.extracted_intel,
            category=session.category or "default"
        )
        
        compliance_style = ScammerBehaviorAnalyzer.get_recommended_compliance(
            scammer_tone, session.turn_count
        )
        
        extraction_strategy = ExtractionGoalTracker.generate_extraction_strategy(
            goal=next_goal,
            scammer_tone=scammer_tone,
            compliance_style=compliance_style
        )
        
        # 5. Get anti-detection instructions
        from .anti_detection import get_analyzer
        analyzer = get_analyzer()
        analysis = analyzer.analyze_history(history)
        avoidance = analyzer.generate_avoidance_instructions(analysis)
        
        # 6. Handle special states
        if ConversationStateAnalyzer.should_have_problems(conversation_state):
            problem = ConversationStateAnalyzer.get_technical_problem(
                session.turn_count,
                "bank" if session.extracted_intel.get("bankAccounts") else "upi"
            )
            extraction_strategy += f"\n\n💡 You can mention this problem: '{problem}' and ask for alternative method."
        
        if ConversationStateAnalyzer.should_stall(conversation_state):
            excuse = ConversationStateAnalyzer.get_stalling_excuse(session.turn_count)
            extraction_strategy = f"STALLING PHASE: Use excuses to delay. Example: '{excuse}'"
        
        # 7. Get emotional hint
        primary_emotion = persona_traits.get("primary_emotion", "confused")
        emotion_hint = cls.EMOTION_HINTS.get(primary_emotion, cls.EMOTION_HINTS["confused"])
        
        # 8. Get emotional state description
        emotional_state = DynamicPersonaGenerator.get_emotional_state_description(persona_traits)
        
        # 9. Build the prompt
        prompt = cls.BASE_TEMPLATE.format(
            character_description=persona_traits.get("character_summary", "Confused person trying to understand"),
            emotional_state=emotional_state,
            communication_style=persona_traits.get("communication_style", "Casual with some typos"),
            scam_type=cls._get_human_readable_category(session.category),
            conversation_phase=f"{conversation_state} - {state_info.get('description', '')}",
            scammer_behavior=f"{scammer_tone.upper()} - {last_exchange_summary}",
            recent_history=cls.format_history(history),
            latest_message=latest_message[:300],  # Truncate very long messages
            last_exchange_summary=last_exchange_summary,
            extraction_strategy=extraction_strategy,
            emotion_hint=emotion_hint,
            forbidden_phrases=avoidance if avoidance else "None - previous responses were good"
        )
        
        return prompt
    
    @classmethod
    def _get_human_readable_category(cls, category: Optional[str]) -> str:
        """Convert internal category to human-readable form"""
        if not category:
            return "Unknown situation"
        
        mappings = {
            "digital_arrest": "Someone claiming to be police/CBI threatening arrest",
            "job_fraud": "Someone offering a job opportunity",
            "lottery_prize": "Someone saying you won a lottery/prize",
            "investment": "Someone offering investment opportunity",
            "romance_dating": "Online romantic interest asking for help",
            "tech_support": "Someone claiming to be tech support",
            "loan_fraud": "Someone offering quick loan",
            "kyc_fraud": "Someone claiming to be from bank about KYC"
        }
        
        category_key = category.lower().replace(" ", "_").replace("-", "_")
        return mappings.get(category_key, f"Someone contacting about: {category}")


# Backward compatibility
PromptBuilder = AdaptivePromptBuilder