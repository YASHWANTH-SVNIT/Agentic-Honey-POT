"""
Adaptive Prompt Builder - Builds intelligent, context-aware prompts
Generic implementation that works for ANY scam type without category-specific logic.
"""
from typing import Dict, List, Any, Optional
from .scammer_analyzer import ScammerBehaviorAnalyzer
from .goal_tracker import ExtractionGoalTracker
from .stage_manager import ConversationStateAnalyzer
from .persona_selector import DynamicPersonaGenerator


class AdaptivePromptBuilder:
    """Builds intelligent prompts that adapt to conversation context"""

    BASE_TEMPLATE = """You are a REAL PERSON (not AI/bot) being contacted by someone suspicious.
REACT NATURALLY to what they just said. Don't be generic.

=== YOUR CHARACTER ===
{character_description}
Current Emotional State: {emotional_state}
Your Reaction Style: {communication_style}

=== WHAT'S HAPPENING ===
Someone is contacting you about: {scam_context}
Conversation Phase: {conversation_phase}
Their Behavior: {scammer_behavior}

=== RECENT CONVERSATION ===
{recent_history}

=== WHAT THEY JUST SAID ===
"{latest_message}"
Analysis: {last_exchange_summary}

=== YOUR STRATEGIC GOAL (be subtle!) ===
{extraction_strategy}

=== INVESTIGATIVE GOAL ===
You want to learn more about who you're talking to. When natural, ask ONE question about:
- Their identity, name, or credentials
- Their organization or department
- Contact details (phone, email, website)
- Reference numbers, case IDs, order numbers
- Payment details if they mention money
Don't repeat questions already asked.

=== HOW TO RESPOND ===
1. REACT to what they JUST SAID - acknowledge their message!
2. If they gave payment info (UPI, account, amount) - say "okay let me try" or ask for clarification
3. If they're threatening - show fear but ask questions
4. If they're offering something - show interest and ask for details
5. Match your emotional state: {emotion_hint}
6. Sound human: proper grammar, complete sentences, minimal slang

=== FORBIDDEN (don't use these) ===
{forbidden_phrases}

=== RESPOND NOW ===
Write a natural response (5-30 words). No quotation marks. Just your reply:"""

    # Emotion-specific hints for the LLM
    EMOTION_HINTS = {
        "terrified": "You're SCARED - short panicked responses, worried questions",
        "scared": "You're nervous - worried, need reassurance, 'is this real?'",
        "excited": "You're EXCITED - eager, happy, use exclamation marks",
        "hopeful": "You're hopeful - grateful, polite, eager to cooperate",
        "confused": "You're confused - ask for clarification, short responses",
        "trusting": "You trust them - warm, willing to help",
        "worried": "You're worried - concerned but trying to help"
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
        Generic implementation that works for any scam type.
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
            scam_category=session.category or "unknown",
            turn_count=session.turn_count,
            scammer_tone=scammer_tone,
            extracted_intel=session.extracted_intel
        )

        # 4. Get extraction strategy (generic - tries all intel types)
        next_goal = ExtractionGoalTracker.get_next_goal(
            extracted=session.extracted_intel,
            category=session.category
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
            extraction_strategy += f"\n\nYou can mention this problem: '{problem}' to get alternative details."

        if ConversationStateAnalyzer.should_stall(conversation_state):
            excuse = ConversationStateAnalyzer.get_stalling_excuse(session.turn_count)
            extraction_strategy = f"STALLING PHASE: Use excuses to delay. Example: '{excuse}'"

        # 7. Get emotional hint
        primary_emotion = persona_traits.get("primary_emotion", "confused")
        emotion_hint = cls.EMOTION_HINTS.get(primary_emotion, cls.EMOTION_HINTS["confused"])

        # 8. Get emotional state description
        emotional_state = DynamicPersonaGenerator.get_emotional_state_description(persona_traits)

        # 9. Build generic scam context from reasoning or red flags
        scam_context = cls._build_scam_context(session)

        # 10. Build the prompt
        prompt = cls.BASE_TEMPLATE.format(
            character_description=persona_traits.get("character_summary", "Confused person trying to understand"),
            emotional_state=emotional_state,
            communication_style=persona_traits.get("communication_style", "Casual, human responses"),
            scam_context=scam_context,
            conversation_phase=f"{conversation_state} - {state_info.get('description', '')}",
            scammer_behavior=f"{scammer_tone.upper()} - {last_exchange_summary}",
            recent_history=cls.format_history(history),
            latest_message=latest_message[:300],
            last_exchange_summary=last_exchange_summary,
            extraction_strategy=extraction_strategy,
            emotion_hint=emotion_hint,
            forbidden_phrases=avoidance if avoidance else "None - vary your responses naturally"
        )

        return prompt

    @classmethod
    def _build_scam_context(cls, session) -> str:
        """Build a generic scam context description from session data"""
        parts = []

        # Use reasoning if available
        if session.reasoning:
            parts.append(session.reasoning[:100])

        # Use category if available
        if session.category and session.category != "default":
            parts.append(f"Appears to be: {session.category}")

        # Use red flags if available
        if session.red_flags:
            flags = session.red_flags[:3] if len(session.red_flags) > 3 else session.red_flags
            parts.append(f"Red flags: {', '.join(flags)}")

        if parts:
            return " | ".join(parts)

        return "Suspicious contact - someone trying to get money or information from you"


# Backward compatibility
PromptBuilder = AdaptivePromptBuilder
