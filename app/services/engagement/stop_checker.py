from typing import Dict, Any, List
from app.models.session import SessionData
from app.services.engagement.stage_manager import StageManager
from config.extraction_targets import get_targets_for_category

class StopConditionChecker:
    
    @staticmethod
    def should_stop(session: SessionData) -> bool:
        """
        Determines if the conversation should end based on:
        1. Turn count limit (Phase 6.2)
        2. Intelligence objectives met (Phase 6.1)
        """
        
        # 1. Maximum Turns Reached
        if session.turn_count >= 15:
            print(f"[StopCheck] Max turns reached ({session.turn_count})")
            return True
            
        # 2. Intelligence Objectives Met
        # Check if we have extracted ALL critical targets for this category
        targets = get_targets_for_category(session.category)
        if targets:
            extracted_keys = session.extracted_intel.keys()
            missing = [t for t in targets if t not in extracted_keys]
            
            # If we turn count is at least 8 AND we have all targets, we can stop
            if not missing and session.turn_count >= 8:
                 print(f"[StopCheck] All intelligence targets met: {targets}")
                 return True
                 
        return False
