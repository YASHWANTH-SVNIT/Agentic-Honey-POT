"""
Generic Extraction Goal Tracker - Category-Agnostic Intelligence Extraction

This tracker attempts to extract ALL possible intelligence types from ANY scam,
regardless of the detected category. The LLM-based InvestigatorAgent decides
what's actually present - we just ensure nothing is missed.
"""
from typing import Dict, List, Optional, Any
import random


class ExtractionGoalTracker:
    """
    Generic extraction tracker that targets ALL intelligence types.
    No category-specific filtering - extract everything possible.
    """

    # ALL intelligence types we can extract - always try all of them
    ALL_TARGETS = [
        "upiIds",
        "phoneNumbers",
        "bankAccounts",
        "bankNames",
        "ifscCodes",
        "amounts",
        "phishingLinks",
        "emailAddresses",
        "caseIds",
        "policyNumbers",
        "orderNumbers"
    ]

    # Generic extraction strategies for ALL intel types
    # These work regardless of scam category
    EXTRACTION_STRATEGIES = {
        "upiIds": {
            "eager": [
                "ok where do i send the money?",
                "which upi id should i pay to?",
                "im ready to pay, whats the upi?",
                "give me the payment details"
            ],
            "hesitant": [
                "umm so where exactly do i transfer?",
                "can you tell me the upi id again?",
                "wait let me note down the upi properly"
            ],
            "confused": [
                "sorry which upi id?",
                "i didnt get it... where to send?",
                "can you type the upi slowly?"
            ]
        },
        "phoneNumbers": {
            "eager": [
                "whats your number in case something goes wrong?",
                "can i call you if theres a problem?",
                "give me a number to reach you"
            ],
            "hesitant": [
                "what if payment fails... how do i contact you?",
                "do you have a helpline number?",
                "i might need to call... whats your number?"
            ],
            "confused": [
                "wait what if i do something wrong... how do i call?",
                "this is confusing... can i just call you?",
                "can you give me a number to call?"
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
                "i think upi has problem... can i transfer to bank?",
                "upi is showing error... what else can i do?"
            ],
            "confused": [
                "i dont know how to use upi... can i do normal transfer?",
                "this upi thing is complicated... bank account?",
                "my son does upi... can i just send to bank?"
            ]
        },
        "bankNames": {
            "eager": [
                "which bank is this account in?",
                "is this sbi or hdfc?",
                "what bank should i transfer to?"
            ],
            "hesitant": [
                "wait which bank did you say?",
                "i need bank name for transfer..."
            ],
            "confused": [
                "sorry which bank?",
                "i need to know the bank name"
            ]
        },
        "ifscCodes": {
            "eager": [
                "whats the ifsc code?",
                "i need ifsc for bank transfer",
                "give me ifsc code also"
            ],
            "hesitant": [
                "my bank is asking ifsc code...",
                "i need ifsc to transfer"
            ],
            "confused": [
                "it says enter ifsc... what is that?",
                "bank app asking for ifsc?"
            ]
        },
        "amounts": {
            "eager": [
                "how much exactly do i need to send?",
                "tell me the exact amount",
                "what is the total i need to pay?"
            ],
            "hesitant": [
                "wait how much money?",
                "thats a lot... are you sure?",
                "i need to check if i have that much..."
            ],
            "confused": [
                "sorry how much again?",
                "i didnt understand the amount...",
                "can you tell me in simple numbers?"
            ]
        },
        "phishingLinks": {
            "eager": [
                "what website do i go to?",
                "can you send me the link?",
                "where do i click?"
            ],
            "hesitant": [
                "is there a website i can check?",
                "do you have an official link?",
                "where can i verify this online?"
            ],
            "confused": [
                "sorry where do i go?",
                "whats the website address?",
                "can you send the link again?"
            ]
        },
        "emailAddresses": {
            "eager": [
                "whats your email for documents?",
                "where do i send the details?",
                "give me email id"
            ],
            "hesitant": [
                "do you have an email i can write to?",
                "can you email me the details?",
                "is there an official email?"
            ],
            "confused": [
                "can you send email?",
                "what is your email id?",
                "i prefer email... whats yours?"
            ]
        },
        "caseIds": {
            "eager": [
                "what is the case number?",
                "give me reference number for records",
                "whats the complaint id?"
            ],
            "hesitant": [
                "can i get a reference number?",
                "is there a case id i should note?",
                "what number do i quote if i call back?"
            ],
            "confused": [
                "sorry what was the case number?",
                "i need to tell my family... whats the reference?",
                "what id should i remember?"
            ]
        },
        "policyNumbers": {
            "eager": [
                "what is the policy number?",
                "give me scheme registration number",
                "whats my policy id?"
            ],
            "hesitant": [
                "can you tell me the policy number?",
                "i should note down the scheme id...",
                "what is the registration number?"
            ],
            "confused": [
                "sorry what policy?",
                "which scheme number?",
                "i dont remember my policy id..."
            ]
        },
        "orderNumbers": {
            "eager": [
                "what is the order number?",
                "give me tracking id",
                "whats the reference for my order?"
            ],
            "hesitant": [
                "can you confirm the order number?",
                "what was the tracking number?",
                "i need order id to check"
            ],
            "confused": [
                "sorry which order?",
                "i have many orders... which one?",
                "whats the order reference?"
            ]
        }
    }

    @classmethod
    def get_targets_for_category(cls, category: str) -> List[str]:
        """
        Always return ALL targets - we want to extract everything possible.
        Category is ignored - the LLM decides what's actually present.
        """
        return cls.ALL_TARGETS.copy()

    @classmethod
    def get_missing_intel(cls, extracted: Dict[str, Any], category: str = None) -> List[str]:
        """Get list of intel types we still need (from ALL types)"""
        missing = []

        for target in cls.ALL_TARGETS:
            current_value = extracted.get(target, [])
            # Consider it missing if empty or not present
            if not current_value or (isinstance(current_value, list) and len(current_value) == 0):
                missing.append(target)

        return missing

    @classmethod
    def get_next_goal(cls, extracted: Dict[str, Any], category: str = None) -> Optional[str]:
        """
        Get the next priority extraction goal.
        Prioritizes payment-related info first, then contact info, then references.
        """
        missing = cls.get_missing_intel(extracted, category)

        if not missing:
            return None

        # Priority order for extraction
        priority = [
            "amounts",        # Most important - what they want
            "upiIds",         # Primary payment method
            "phoneNumbers",   # Contact for follow-up
            "bankAccounts",   # Alternative payment
            "phishingLinks",  # Websites to report
            "emailAddresses", # Contact info
            "caseIds",        # Reference numbers
            "bankNames",      # Bank details
            "ifscCodes",      # Bank details
            "orderNumbers",   # References
            "policyNumbers"   # References
        ]

        for target in priority:
            if target in missing:
                return target

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
            return "You have gathered good information. Stall naturally - 'wait one sec', 'my phone is slow', 'let me check my balance'."

        strategies = cls.EXTRACTION_STRATEGIES.get(goal, {})

        # Pick strategy based on compliance style
        if compliance_style not in strategies:
            compliance_style = "hesitant"

        options = strategies.get(compliance_style, ["ok what do i do next?"])
        strategy = random.choice(options)

        # Add context based on scammer tone
        if scammer_tone == "aggressive":
            return f"Scammer is AGGRESSIVE. Show fear, comply quickly. Try to ask: '{strategy}'"
        elif scammer_tone == "patient":
            return f"Scammer is patient. You can ask questions naturally. Example: '{strategy}'"
        elif scammer_tone == "frustrated":
            return f"Scammer is getting frustrated. Be apologetic but still ask: '{strategy}'"
        else:
            return f"Extract naturally by asking something like: '{strategy}'"

    @classmethod
    def get_extraction_progress(cls, extracted: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Get extraction progress summary"""
        all_targets = cls.ALL_TARGETS
        missing = cls.get_missing_intel(extracted, category)

        # Count how many we've actually extracted (non-empty)
        extracted_targets = []
        for target in all_targets:
            value = extracted.get(target, [])
            if value and (not isinstance(value, list) or len(value) > 0):
                extracted_targets.append(target)

        extracted_count = len(extracted_targets)
        total = len(all_targets)
        percentage = (extracted_count / total * 100) if total > 0 else 0

        return {
            "extracted": extracted_targets,
            "missing": missing,
            "percentage": percentage,
            "next_goal": cls.get_next_goal(extracted, category),
            "total_types": total,
            "extracted_count": extracted_count
        }
