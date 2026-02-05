"""
Conversation State Analyzer - Determines conversation phase based on CONTENT, not turn count
No more static stage_config.json - states are determined dynamically
"""
from typing import Dict, List, Any, Optional


class ConversationStateAnalyzer:
    """Analyzes conversation to determine current state based on content, not turns"""
    
    # Conversation states - based on WHAT'S HAPPENING, not turn number
    STATES = {
        "initial_shock": {
            "description": "First contact - confused, asking what's happening",
            "behavior": "Confused, scared (if threat) or excited (if prize), asking basic questions",
            "goal": "Understand the situation, show initial reaction"
        },
        "understanding": {
            "description": "Understanding the threat/opportunity - asking clarifying questions",
            "behavior": "Still processing, asking 'what do I need to do?', 'is this real?'",
            "goal": "Get scammer to explain more, reveal details"
        },
        "compliance_ready": {
            "description": "Convinced and ready to act - asking HOW to comply",
            "behavior": "Willing to act, asking for payment details, contact info",
            "goal": "Extract payment methods, contact information"
        },
        "attempting_action": {
            "description": "Actively trying to comply - 'trying to send money'",
            "behavior": "Says they're trying, may report small issues",
            "goal": "Confirm details, set up for 'technical difficulties'"
        },
        "technical_difficulties": {
            "description": "Having 'problems' with payment/action - asking for alternatives",
            "behavior": "Frustrated with tech, asking for other payment methods, backup contact",
            "goal": "Extract ADDITIONAL payment methods, backup info"
        },
        "exhaustion_stalling": {
            "description": "Tired, slow, distracted - stalling naturally",
            "behavior": "Slow responses, mentions being tired, distractions (doorbell, kids, etc.)",
            "goal": "Waste scammer's time, graceful exit"
        }
    }
    
    @classmethod
    def determine_state(
        cls,
        history: List[Dict[str, str]],
        extracted_intel: Dict[str, Any],
        turn_count: int,
        scammer_tone: str = "neutral"
    ) -> str:
        """
        Determine conversation state based on content and context.
        This replaces turn-based stage progression.
        """
        
        # Count how much intel we have
        intel_count = sum(1 for v in extracted_intel.values() if (isinstance(v, list) and len(v) > 0) or (not isinstance(v, list) and v))
        
        has_upi = bool(extracted_intel.get("upiIds"))
        has_phone = bool(extracted_intel.get("phoneNumbers"))
        has_bank = bool(extracted_intel.get("bankAccounts"))
        has_amount = bool(extracted_intel.get("amounts"))
        
        payment_info_count = sum([has_upi, has_phone, has_bank])
        
        # State determination logic (content-based)
        
        # End game conditions
        if turn_count >= 15:
            return "exhaustion_stalling"
        
        if payment_info_count >= 3:
            # Got most payment info - start stalling
            return "exhaustion_stalling"
        
        if payment_info_count >= 2:
            # Got some payment info - have "technical difficulties" to get more
            return "technical_difficulties"
        
        if payment_info_count >= 1:
            # Got one payment method - try to "use it" (and fail)
            return "attempting_action"
        
        if has_amount and turn_count >= 3:
            # Know what to pay but not where - ask for details
            return "compliance_ready"
        
        # Early conversation states
        if turn_count <= 2:
            return "initial_shock"
        
        if turn_count <= 4:
            return "understanding"
        
        # Default to compliance ready (agent should be trying to extract)
        return "compliance_ready"
    
    @classmethod
    def get_state_info(cls, state: str) -> Dict[str, str]:
        """Get information about a conversation state"""
        return cls.STATES.get(state, cls.STATES["understanding"])
    
    @classmethod
    def get_state_behavior(cls, state: str) -> str:
        """Get the expected behavior for a state"""
        state_info = cls.get_state_info(state)
        return state_info.get("behavior", "Confused but trying to understand")
    
    @classmethod
    def get_state_goal(cls, state: str) -> str:
        """Get the goal for a state"""
        state_info = cls.get_state_info(state)
        return state_info.get("goal", "Extract information naturally")
    
    @classmethod
    def should_have_problems(cls, state: str) -> bool:
        """Check if the agent should be experiencing 'technical difficulties'"""
        return state in ["attempting_action", "technical_difficulties"]
    
    @classmethod
    def should_stall(cls, state: str) -> bool:
        """Check if the agent should be stalling"""
        return state == "exhaustion_stalling"
    
    @classmethod
    def get_stalling_excuse(cls, turn_count: int) -> str:
        """Get a natural stalling excuse"""
        excuses = [
            "wait one sec someone is at the door",
            "hold on my kids are calling me",
            "my phone battery is low let me find charger",
            "the internet is very slow here",
            "wait i need to ask my husband/wife",
            "let me try from my other phone",
            "the otp is not coming to my phone",
            "i need to go to the bank to get my phone registered",
            "my son usually does these things let me call him",
            "wait i think my app needs update"
        ]
        return excuses[turn_count % len(excuses)]
    
    @classmethod
    def get_technical_problem(cls, turn_count: int, last_method: str = "upi") -> str:
        """Get a natural technical problem excuse"""
        
        upi_problems = [
            "its showing invalid upi id error",
            "the app says 'transaction failed'",
            "payment is stuck at processing",
            "it says 'vpa not found'",
            "my upi app crashed",
            "says 'bank server down'"
        ]
        
        bank_problems = [
            "bank website is not loading",
            "it says 'invalid account number'",
            "my net banking otp is not coming",
            "website says 'try again later'",
            "i cant remember my net banking password"
        ]
        
        if last_method == "bank":
            return bank_problems[turn_count % len(bank_problems)]
        else:
            return upi_problems[turn_count % len(upi_problems)]


# Backward compatibility aliases
StageManager = ConversationStateAnalyzer
