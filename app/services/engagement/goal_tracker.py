"""
Extraction Goal Tracker - Tracks what intel we have and what we still need
Provides strategic extraction approaches for natural information gathering
"""
from typing import Dict, List, Optional, Any
import random


class ExtractionGoalTracker:
    """Tracks extraction goals and generates natural extraction strategies"""
    
    # What we want to extract per scam category
    EXTRACTION_TARGETS = {
        "digital_arrest": ["upiIds", "phoneNumbers", "bankAccounts", "amounts", "officerNames"],
        "job_fraud": ["upiIds", "phoneNumbers", "companyNames", "amounts", "emailIds"],
        "lottery_prize": ["upiIds", "phoneNumbers", "bankAccounts", "amounts", "claimNumbers"],
        "investment": ["upiIds", "phoneNumbers", "bankAccounts", "amounts", "platformNames"],
        "romance_dating": ["phoneNumbers", "bankAccounts", "amounts", "socialProfiles"],
        "tech_support": ["upiIds", "phoneNumbers", "amounts", "websiteLinks"],
        "loan_fraud": ["upiIds", "phoneNumbers", "bankAccounts", "amounts"],
        "kyc_fraud": ["upiIds", "phoneNumbers", "bankAccounts", "aadharNumbers"],
        "default": ["upiIds", "phoneNumbers", "bankAccounts", "amounts"]
    }
    
    # Natural ways to ask for each type of info (context-dependent)
    EXTRACTION_STRATEGIES = {
        "upiIds": {
            "eager": [
                "ok where do i send the money??",
                "which upi id should i pay to?",
                "ok im ready to pay, give me the details"
            ],
            "hesitant": [
                "umm so where exactly do i transfer?",
                "ok but which upi... i need to be sure",
                "wait let me note down the upi id properly"
            ],
            "confused": [
                "sorry im confused... which upi id again?",
                "i didnt get it... where to send?",
                "can u type the upi id slowly plz"
            ]
        },
        "phoneNumbers": {
            "eager": [
                "what if something goes wrong, whats your number?",
                "can i call you if theres a problem?",
                "give me a number to reach you"
            ],
            "hesitant": [
                "umm what if the payment fails... how do i contact you?",
                "do you have a helpline number or something?",
                "i might need to call... whats your number?"
            ],
            "confused": [
                "wait what if i do something wrong... how do i call you?",
                "this is confusing... can i just call you instead?",
                "i dont understand... can u give me a number to call?"
            ]
        },
        "bankAccounts": {
            "eager": [
                "my upi is giving error... can i do bank transfer?",
                "upi not working, give me account number",
                "let me try bank transfer instead"
            ],
            "hesitant": [
                "umm my upi app crashed... is there another way?",
                "i think upi has some problem... can i transfer to bank?",
                "upi is showing error... what else can i do?"
            ],
            "confused": [
                "i dont know how to use upi properly... can i do normal transfer?",
                "this upi thing is too complicated... bank account?",
                "my son usually does upi... can i just send to bank?"
            ]
        },
        "amounts": {
            "eager": [
                "how much exactly do i need to send?",
                "ok tell me the exact amount",
                "what is the total i need to pay?"
            ],
            "hesitant": [
                "wait how much money are we talking about?",
                "thats a lot of money... are you sure?",
                "i need to check if i have that much..."
            ],
            "confused": [
                "sorry how much again?",
                "i didnt understand the amount...",
                "can u tell me in simple numbers?"
            ]
        },
        "officerNames": {
            "eager": [
                "ok sir what is your name and badge number?",
                "can i know who im talking to?",
                "what department are you from?"
            ],
            "hesitant": [
                "umm can i know your name sir?",
                "which officer should i ask for if i call back?",
                "what is your designation?"
            ],
            "confused": [
                "sorry who am i talking to?",
                "i need to tell my family... whats your name?",
                "which department is this?"
            ]
        }
    }
    
    @classmethod
    def get_targets_for_category(cls, category: str) -> List[str]:
        """Get extraction targets for a scam category"""
        return cls.EXTRACTION_TARGETS.get(category, cls.EXTRACTION_TARGETS["default"])
    
    @classmethod
    def get_missing_intel(cls, extracted: Dict[str, Any], category: str) -> List[str]:
        """Get list of intel types we still need"""
        targets = cls.get_targets_for_category(category)
        missing = []
        
        for target in targets:
            current_value = extracted.get(target, [])
            # Consider it missing if empty or not present
            if not current_value or (isinstance(current_value, list) and len(current_value) == 0):
                missing.append(target)
        
        return missing
    
    @classmethod
    def get_next_goal(cls, extracted: Dict[str, Any], category: str) -> Optional[str]:
        """Get the next priority extraction goal"""
        missing = cls.get_missing_intel(extracted, category)
        return missing[0] if missing else None
    
    @classmethod
    def generate_extraction_strategy(
        cls, 
        goal: Optional[str], 
        scammer_tone: str,
        compliance_style: str = "hesitant"
    ) -> str:
        """Generate a natural way to extract the next piece of info"""
        
        if not goal:
            return "You have extracted most information. Stall naturally - 'wait one sec', 'my phone is slow', etc."
        
        strategies = cls.EXTRACTION_STRATEGIES.get(goal, {})
        
        # Pick strategy based on compliance style
        if compliance_style not in strategies:
            compliance_style = "hesitant"
        
        options = strategies.get(compliance_style, ["ok what do i do next?"])
        
        # Add context based on scammer tone
        strategy = random.choice(options)
        
        if scammer_tone == "aggressive":
            return f"Scammer is AGGRESSIVE. Show fear, comply quickly. Example: '{strategy}'"
        elif scammer_tone == "patient":
            return f"Scammer is patient. You can ask more questions. Example: '{strategy}'"
        else:
            return f"Extract naturally. Example: '{strategy}'"
    
    @classmethod
    def get_extraction_progress(cls, extracted: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Get extraction progress summary"""
        targets = cls.get_targets_for_category(category)
        missing = cls.get_missing_intel(extracted, category)
        
        extracted_count = len(targets) - len(missing)
        total = len(targets)
        percentage = (extracted_count / total * 100) if total > 0 else 0
        
        return {
            "extracted": [t for t in targets if t not in missing],
            "missing": missing,
            "percentage": percentage,
            "next_goal": missing[0] if missing else None
        }
