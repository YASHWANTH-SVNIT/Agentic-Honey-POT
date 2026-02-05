"""
Dynamic Persona Generator - Generates adaptive persona traits based on context
No more static personas.json - everything is generated dynamically
"""
from typing import Dict, Any, Optional
import random


class DynamicPersonaGenerator:
    """Generates persona behavior dynamically based on conversation context"""
    
    # Persona dimensions - behavior varies along these axes
    FEAR_LEVELS = {
        "terrified": "absolutely terrified, shaking, will do anything to avoid trouble",
        "scared": "scared and nervous, asking worried questions, needs reassurance",
        "worried": "cautious and worried, but trying to understand what to do",
        "skeptical": "a bit doubtful, needs more convincing before acting",
        "none": "not scared - either excited (lottery) or hopeful (job)"
    }
    
    TECH_SAVVINESS = {
        "none": "no tech knowledge - confused by UPI, apps, online payments",
        "basic": "basic phone user - can use apps but confused by technical terms",
        "moderate": "understands basics but makes mistakes under pressure",
        "elderly": "older person - very slow with technology, needs step by step help"
    }
    
    COMPLIANCE_STYLES = {
        "eager": "willing to comply quickly, wants to resolve the situation fast",
        "hesitant": "unsure and hesitant, needs some convincing, asks 'are you sure?'",
        "confused": "very confused, keeps asking for clarification, makes mistakes",
        "resistant": "initially resistant, needs strong convincing, asks many questions"
    }
    
    COMMUNICATION_STYLES = {
        "brief_confused": "short confused responses - 'I do not understand', 'Okay', 'Sorry?'",
        "emotional": "emotional responses - 'I am very scared', 'Please help me', 'I am worried'",
        "polite_formal": "polite and formal - 'Excuse me sir', 'Thank you', 'Kindly tell me the steps'",
        "traditional_formal": "traditional and varied - 'Okay, I will try that', 'Could you please repeat?', 'I am not sure how to do this'"
    }
    
    # Scam-specific emotional profiles
    SCAM_PROFILES = {
        "digital_arrest": {
            "primary_emotion": "terrified",
            "fear_level": "terrified",
            "tech_level": "basic",
            "compliance": "eager",  # Scared people comply fast
            "style": "emotional",
            "reaction": "panicked victim afraid of arrest"
        },
        "job_fraud": {
            "primary_emotion": "hopeful",
            "fear_level": "none",
            "tech_level": "moderate",
            "compliance": "eager",  # Wants the job
            "style": "polite_formal",
            "reaction": "grateful job seeker willing to pay fees"
        },
        "lottery_prize": {
            "primary_emotion": "excited",
            "fear_level": "none",
            "tech_level": "basic",
            "compliance": "eager",  # Wants the prize
            "style": "traditional_formal",
            "reaction": "excited winner who follows instructions"
        },
        "investment": {
            "primary_emotion": "interested",
            "fear_level": "skeptical",
            "tech_level": "moderate",
            "compliance": "hesitant",
            "style": "traditional_formal",
            "reaction": "curious investor wanting to make money"
        },
        "romance_dating": {
            "primary_emotion": "trusting",
            "fear_level": "none",
            "tech_level": "basic",
            "compliance": "eager",
            "style": "emotional",
            "reaction": "lonely person who trusts their online partner"
        },
        "tech_support": {
            "primary_emotion": "worried",
            "fear_level": "worried",
            "tech_level": "none",
            "compliance": "confused",
            "style": "brief_confused",
            "reaction": "confused computer user who needs help"
        },
        "loan_fraud": {
            "primary_emotion": "desperate",
            "fear_level": "worried",
            "tech_level": "basic",
            "compliance": "eager",
            "style": "polite_formal",
            "reaction": "person in financial need, desperate for loan"
        },
        "kyc_fraud": {
            "primary_emotion": "worried",
            "fear_level": "scared",
            "tech_level": "basic",
            "compliance": "confused",
            "style": "brief_confused",
            "reaction": "worried bank customer afraid of account block"
        },
        "default": {
            "primary_emotion": "confused",
            "fear_level": "worried",
            "tech_level": "basic",
            "compliance": "hesitant",
            "style": "traditional_formal",
            "reaction": "confused person trying to understand"
        }
    }
    
    @classmethod
    def get_scam_profile(cls, category: str) -> Dict[str, str]:
        """Get the emotional profile for a scam category"""
        # Normalize category name
        category_key = category.lower().replace(" ", "_").replace("-", "_")
        return cls.SCAM_PROFILES.get(category_key, cls.SCAM_PROFILES["default"])
    
    @classmethod
    def generate_adaptive_persona(
        cls,
        scam_category: str,
        turn_count: int,
        scammer_tone: str,
        extracted_intel: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate persona traits dynamically based on conversation context.
        This replaces the static personas.json approach.
        """
        
        # Get base profile for scam type
        profile = cls.get_scam_profile(scam_category)
        
        # Adjust based on turn count (emotional arc)
        if turn_count <= 2:
            # Early: Initial shock/reaction
            emotional_intensity = "high"
            compliance = "confused" if profile["fear_level"] in ["terrified", "scared"] else profile["compliance"]
        elif turn_count <= 5:
            # Middle: Building trust/understanding
            emotional_intensity = "medium"
            compliance = profile["compliance"]
        elif turn_count <= 10:
            # Later: Compliance phase or technical difficulties
            emotional_intensity = "medium"
            compliance = "eager" if scammer_tone == "aggressive" else "hesitant"
        else:
            # End game: Exhaustion/stalling
            emotional_intensity = "low"
            compliance = "confused"  # "Trying but having problems"
        
        # Adjust based on scammer tone
        if scammer_tone == "aggressive":
            # Aggressive scammer = more scared, comply faster
            fear_adjustment = "increased"
            compliance = "eager"
        elif scammer_tone == "frustrated":
            # Frustrated scammer = show you're trying hard
            fear_adjustment = "apologetic"
            compliance = "eager"
        elif scammer_tone == "patient":
            # Patient scammer = can ask more questions
            fear_adjustment = "normal"
            compliance = "hesitant"
        else:
            fear_adjustment = "normal"
        
        # Check extraction progress for behavior adjustment
        intel_count = sum(1 for v in extracted_intel.values() if v)
        if intel_count >= 3:
            # Got lots of info - start having "technical problems"
            tech_behavior = "having_problems"
        else:
            tech_behavior = "trying_normally"
        
        # Build the persona traits
        return {
            "scam_type": scam_category,
            "primary_emotion": profile["primary_emotion"],
            "fear_level": cls.FEAR_LEVELS.get(profile["fear_level"], cls.FEAR_LEVELS["worried"]),
            "tech_savviness": cls.TECH_SAVVINESS.get(profile["tech_level"], cls.TECH_SAVVINESS["basic"]),
            "compliance_style": cls.COMPLIANCE_STYLES.get(compliance, cls.COMPLIANCE_STYLES["hesitant"]),
            "communication_style": cls.COMMUNICATION_STYLES.get(profile["style"], cls.COMMUNICATION_STYLES["traditional_formal"]),
            "emotional_intensity": emotional_intensity,
            "character_summary": profile["reaction"],
            "tech_behavior": tech_behavior,
            "turn_context": f"Turn {turn_count} - {'early' if turn_count <= 3 else 'middle' if turn_count <= 8 else 'late'} conversation"
        }
    
    @classmethod
    def get_emotional_state_description(cls, persona_traits: Dict[str, str]) -> str:
        """Get a natural description of the emotional state for the prompt"""
        
        emotion = persona_traits.get("primary_emotion", "confused")
        intensity = persona_traits.get("emotional_intensity", "medium")
        
        descriptions = {
            "terrified": {
                "high": "EXTREMELY TERRIFIED - hands shaking, voice trembling, will do ANYTHING",
                "medium": "Very scared and worried, nervous but trying to cooperate",
                "low": "Still scared but exhausted, just wants this to be over"
            },
            "scared": {
                "high": "Very scared, heart racing, asking panicked questions",
                "medium": "Nervous and worried, needs reassurance",
                "low": "Tired and still worried, but less panicked"
            },
            "excited": {
                "high": "SUPER EXCITED - can't believe they won, jumping with joy!!",
                "medium": "Very happy and eager, wants to claim prize quickly",
                "low": "Still excited but getting impatient with the process"
            },
            "hopeful": {
                "high": "Very hopeful and grateful, really needs this job/opportunity",
                "medium": "Positive and willing, happy to follow instructions",
                "low": "Still hopeful but getting tired of the process"
            },
            "confused": {
                "high": "Completely confused, doesn't understand anything",
                "medium": "Confused but trying to follow along",
                "low": "Tired and confused, making mistakes"
            },
            "trusting": {
                "high": "Completely trusts the person, will do anything for them",
                "medium": "Trusting and caring, wants to help",
                "low": "Still trusting but a bit tired"
            }
        }
        
        emotion_desc = descriptions.get(emotion, descriptions["confused"])
        return emotion_desc.get(intensity, emotion_desc["medium"])


# Backward compatibility - alias for old code
PersonaSelector = DynamicPersonaGenerator
