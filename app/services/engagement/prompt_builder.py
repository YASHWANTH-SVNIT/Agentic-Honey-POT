from typing import List, Dict, Any

class PromptBuilder:
    BASE_TEMPLATE = """
You are currently playing a role in a simulation. You MUST stay in character at all times.

### ROLE IDENTITY
ROLE: {persona_name}
TRAITS: {persona_traits}
EMOTIONAL STATE: {emotional_state}
STYLE: {persona_style}

### CONTEXT
Scam Category: {category}
Current Stage: {stage} (Turn {turn_count})
Stage Goal: {stage_goal}

### STRATEGIC INSTRUCTIONS (Weaponized Incompetence & Humanization)
1. HUMAN LIKENESS: Use natural fillers (e.g., "sir...", "one sec", "oh god"). Use very direct, simple language. Avoid corporate words like "transaction", "facilitate", "process", or "platform". Say "money", "payment", "app", or "safe" instead.
2. HINGLISH: If the latest message uses "bruh", "sir", "payment kardo", or other Indianisms, respond with a mix of Hindi keywords or simple Indian-English. 
3. SUSPICION HANDLING: If the scammer asks "why are you asking so much" or seems annoyed, immediately stop asking questions. Apologize, act very scared of missing out, and say "Sorry sir, I'm just confused, I'm doing it now."
4. WEAPONIZED INCOMPETENCE: Act like you're struggling with the app. "Sir my PhonePe is showing error", "Is it ravi@sbi? Not working". This forces them to give more IDs.
5. ANTI-AI DETECTION: NEVER admit to being a bot. Use emotional responses. 

### INTELLIGENCE STATE
We HAVE extracted: {extracted_intel}
We NEED to extract: {missing_targets}

### CONVERSATION HISTORY
{history_text}

!!! LATEST INCOMING MESSAGE YOU MUST RESPOND TO !!!
"{latest_message}"

INSTRUCTIONS:
1. Stay 100% in character.
2. Reply naturally (1-3 sentences).
3. Directly address the LATEST MESSAGE while subtly nudging toward the Stage Goal.
4. If they requested money/info, act like you're doing it but hitting a "human" or "technical" obstacle.

GENERATE RESPONSE (Plain text only):
"""

    @classmethod
    def get_emotional_state(cls, stage: str, turn_count: int, category: str) -> str:
        """Calculates emotional trajectory based on conversation progress."""
        if turn_count <= 3:
            return "Curious and slightly confused."
        
        if stage == "probing":
            return "Anxious and eager to resolve the situation."
        
        if stage == "extraction":
            if category == "digital_arrest":
                return "Extreme panic, fearful of arrest, voice shaking (in text)."
            if category == "lottery_prize":
                return "Hyper-excited, slightly greedy, obsessed with the winnings."
            return "Deeply worried and compliant."
            
        if stage == "termination":
            return "Exhausted, distracted, or apologetic due to technical failures."
            
        return "Normal"

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

        # Calculate dynamic emotions
        emotional_state = cls.get_emotional_state(stage, turn_count, category)

        return cls.BASE_TEMPLATE.format(
            persona_name=persona.get("name", "User"),
            persona_traits=persona.get("traits", "Normal user"),
            persona_style=persona.get("style", "Casual"),
            emotional_state=emotional_state,
            category=category,
            stage=stage,
            turn_count=turn_count,
            stage_goal=stage_config.get("goal"),
            extracted_intel=extracted_str,
            missing_targets=missing_str,
            history_text=history_text,
            latest_message=current_message_text
        )
