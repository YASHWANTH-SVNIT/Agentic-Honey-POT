from typing import List, Dict, Any
import random
from app.services.engagement.anti_detection import get_analyzer

class PromptBuilder:
    """
    Builds prompts with SHORT, realistic responses (10-20 words max).
    """
    
    BASE_TEMPLATE = """You are a REAL PERSON texting (NOT a chatbot).

CHARACTER:
{persona_name} - {persona_traits}

SITUATION:
Someone claims: {category}
Turn: {turn_count}

RECENT CHAT:
{history_text}

THEIR MESSAGE:
"{latest_message}"

⚠️ AVOID (already used):
{avoidance_instructions}

RESPONSE RULES:

1. ⭐ LENGTH - MOST IMPORTANT:
   {length_instruction}
   
   ✅ GOOD EXAMPLES (10-20 words):
   - "wat?? im really scared right now"
   - "ok but how exactly do i do that"
   - "wait im confused which one"
   - "umm ok i guess... when?"
   
   ❌ BAD (too long):
   - Anything over 25 words
   - Multiple questions in one message
   - Long explanations
   
   👉 AIM FOR 10-20 WORDS TOTAL

2. BE CASUAL:
   - "wat" "u" "r" "gonna" "cant"
   - Typos: "recieve" "definately" "wierd" "beleive"
   - Drop words: "cant believe" not "I can't"
   - Sometimes no caps: "ok i will"

3. BEHAVIOR:
   {behavior_instruction}

RESPOND (10-20 WORDS MAX):"""

    BEHAVIOR_PATTERNS = [
        "Comply quickly - say ok or agree",
        "Delay - say busy or confused",
        "Ask brief question - wat/how/when",
        "Show doubt - is this real?",
        "Get distracted - phone ringing",
        "Show fear - im scared",
        "Confused - dont understand"
    ]
    
    LENGTH_PATTERNS = [
        "VERY SHORT (5-10 words): 'wat??' 'im scared' 'how do i?'",
        "SHORT (10-15 words): One simple sentence",
        "MEDIUM (15-20 words): Two very short sentences",
        "BRIEF (3-5 words): 'umm' 'ok' 'wat' 'really??'"
    ]

    @staticmethod
    def build_history_text(history: List[Dict[str, str]]) -> str:
        text = ""
        for msg in history[-4:]:  # Last 4 only
            sender = msg.get("role", msg.get("sender", ""))
            content = msg.get("content", msg.get("text", ""))
            if sender in ["scammer", "user"]:
                text += f"Them: {content[:40]}...\n"
            else:
                text += f"You: {content[:40]}...\n"
        return text if text else "Start of chat"

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
        
        # Random behavior and length
        behavior = random.choice(cls.BEHAVIOR_PATTERNS)
        length = random.choice(cls.LENGTH_PATTERNS)
        
        # Anti-repetition
        analyzer = get_analyzer()
        analysis = analyzer.analyze_history(history)
        avoidance = analyzer.generate_avoidance_instructions(analysis)

        return cls.BASE_TEMPLATE.format(
            persona_name=persona.get("name", "User"),
            persona_traits=persona.get("traits", "Casual person"),
            category=category,
            turn_count=turn_count,
            history_text=history_text,
            latest_message=current_message_text,
            behavior_instruction=behavior,
            length_instruction=length,
            avoidance_instructions=avoidance
        )