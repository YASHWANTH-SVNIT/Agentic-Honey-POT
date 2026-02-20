"""
Stop Condition Checker - Determines when to end conversations

Generic implementation that doesn't depend on category-specific targets.
"""
from typing import Dict, Any, List
from app.models.session import SessionData
from app.services.engagement.goal_tracker import ExtractionGoalTracker


class StopConditionChecker:

    @staticmethod
    def should_stop(session: SessionData) -> bool:
        """
        Determines if the conversation should end based on:
        1. Turn count limit
        2. Sufficient intelligence gathered
        """

        # 1. Maximum Turns Reached (hard limit)
        if session.turn_count >= 15:
            print(f"[StopCheck] Max turns reached ({session.turn_count})")
            return True

        # 2. Check extraction progress
        progress = ExtractionGoalTracker.get_extraction_progress(
            extracted=session.extracted_intel,
            category=session.category
        )

        # If we have at least 8 turns AND extracted 4+ different intel types, we can stop
        if session.turn_count >= 8 and progress["extracted_count"] >= 4:
            print(f"[StopCheck] Good extraction progress: {progress['extracted_count']} types extracted")
            return True

        # 3. If we've extracted payment info (UPI/bank) + contact info, that's usually enough
        extracted = session.extracted_intel
        has_payment = bool(extracted.get("upiIds") or extracted.get("bankAccounts"))
        has_contact = bool(extracted.get("phoneNumbers") or extracted.get("emailAddresses"))
        has_amount = bool(extracted.get("amounts"))

        if session.turn_count >= 6 and has_payment and has_contact and has_amount:
            print(f"[StopCheck] Core intelligence gathered (payment + contact + amount)")
            return True

        return False


# Backward compatibility alias
StopChecker = StopConditionChecker
