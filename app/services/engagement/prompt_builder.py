from typing import List, Dict, Any

class PromptBuilder:
    BASE_TEMPLATE = """
You are currently playing a role in a simulation.
ROLE: {persona_name}
TRAITS: {persona_traits}
STYLE: {persona_style}

CONTEXT:
Scam Category: {category}
Current Stage: {stage} (Turn {turn_count})
Stage Goal: {stage_goal}
Stage Response Style: {stage_style}

INTELLIGENCE STATE:
We HAVE extracted: {extracted_intel}
We NEED to extract: {missing_targets}

CONVERSATION HISTORY:
{history_text}

!!! LATEST INCOMING MESSAGE YOU MUST RESPOND TO !!!
"{latest_message}"

INSTRUCTIONS:
1. Stay 100% in character. Never admit you are an AI or 'honeypot'.
2. Your goal is to keep the conversation going to achieve the 'Stage Goal'.
3. Do NOT provide real personal info. Make up believable fake details if asked.
4. Reply naturally, matching the persona's fear/greed/curiosity level.
5. If in 'Probing' or 'Extraction' stage, subtly steer towards getting the 'missing_targets'.
6. Keep response short (1-3 sentences) unless the persona is defined as over-sharing.
7. CRITICAL: Address the LATEST MESSAGE directly. If they asked for money, stall or ask how to pay. If they asked for bank, act confused or give a fake name. Do NOT just repeat old questions.

GENERATE RESPONSE (Plain text only):
"""

    @staticmethod
    def build_history_text(history: List[Dict[str, str]]) -> str:
        text = ""
        # Take last 10 messages max to fit context
        for msg in history[-10:]:
            sender = msg.get("role", msg.get("sender", "unknown"))
            content = msg.get("content", msg.get("text", ""))
            text += f"{sender}: {content}\n"
        return text

    @classmethod
    def create_prompt(
        cls,
        persona: Dict[str, str],
        category: str,
        stage: str,
        stage_config: Dict[str, Any],
        turn_count: int,
        extracted_intel: Dict[str, Any],
        missing_targets: List[str],
        history: List[Dict[str, str]],
        current_message_text: str
    ) -> str:
        
        history_text = cls.build_history_text(history)
        
        # Format the missing targets nicely
        missing_str = ", ".join(missing_targets) if missing_targets else "None (Keep engaging)"
        extracted_str = ", ".join(extracted_intel.keys()) if extracted_intel else "None"

        return cls.BASE_TEMPLATE.format(
            persona_name=persona.get("name", "User"),
            persona_traits=persona.get("traits", "Normal user"),
            persona_style=persona.get("style", "Casual"),
            category=category,
            stage=stage,
            turn_count=turn_count,
            stage_goal=stage_config.get("goal"),
            stage_style=stage_config.get("response_style"),
            extracted_intel=extracted_str,
            missing_targets=missing_str,
            history_text=history_text,
            latest_message=current_message_text
        )
