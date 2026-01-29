from typing import Dict, Any

class StageManager:
    STAGES = {
        "engagement": {
            "range": (1, 3),
            "goal": "Build trust, show interest, confirming the scam context without raising suspicion.",
            "response_style": "Curious, concerned, asking basic clarifying questions."
        },
        "probing": {
            "range": (4, 7),
            "goal": "Express willingness to proceed but 'encountering issues' or needing details to move forward.",
            "response_style": "Willing but incompetent, asking for specific details to 'help' complete the task."
        },
        "extraction": {
            "range": (8, 12),
            "goal": "actively request specific actionable details (UPI, URL, Bank Account) under the guise of compliance.",
            "response_style": "Ready to act, requesting exact steps/details to finalize the 'transaction'."
        },
        "termination": {
            "range": (13, 100),
            "goal": "Stall indefinitely, make excuses, or stop responding if extraction is complete.",
            "response_style": "Stalling, technical issues, excuses, delays."
        }
    }

    @classmethod
    def determine_stage(cls, turn_count: int) -> str:
        """
        Determines the current conversation stage based on the turn count.
        """
        for stage, config in cls.STAGES.items():
            start, end = config["range"]
            if start <= turn_count <= end:
                return stage
        return "termination"  # Default fallback

    @classmethod
    def get_stage_config(cls, stage: str) -> Dict[str, Any]:
        return cls.STAGES.get(stage, cls.STAGES["termination"])
