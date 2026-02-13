"""
Session-based logging utility for evaluation tracking.
Creates one JSON file per session with complete conversation history.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class SessionLogger:
    """Logs each session's conversation to a separate JSON file."""
    
    LOG_DIR = Path("/tmp/evaluation_logs")
    
    @classmethod
    def _ensure_log_dir(cls):
        """Create log directory if it doesn't exist."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def _get_log_path(cls, session_id: str) -> Path:
        """Get the file path for a session's log."""
        cls._ensure_log_dir()
        # Sanitize session ID for filename
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ('-', '_'))
        return cls.LOG_DIR / f"session_{safe_id}.json"
    
    @classmethod
    def _load_session_log(cls, session_id: str) -> Dict[str, Any]:
        """Load existing session log or create new one."""
        log_path = cls._get_log_path(session_id)
        
        if log_path.exists():
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Corrupted file, start fresh
                pass
        
        # Create new session log
        return {
            "sessionId": session_id,
            "started": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "totalTurns": 0,
            "scamDetected": False,
            "turns": [],
            "finalIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": [],
                "amounts": [],
                "bankNames": [],
                "ifscCodes": []
            }
        }
    
    @classmethod
    def log_turn(
        cls,
        session_id: str,
        scammer_message: str,
        honeypot_reply: str,
        scam_detected: bool,
        intelligence: Dict[str, List[str]],
        action: str = "probe",
        notes: str = ""
    ):
        """
        Log a single turn in the conversation.
        
        Args:
            session_id: Unique session identifier
            scammer_message: The scammer's message
            honeypot_reply: The honeypot's response
            scam_detected: Whether scam was detected
            intelligence: Extracted intelligence from this turn
            action: Agent action (probe, engage, terminate)
            notes: Additional notes
        """
        try:
            # Load existing or create new
            session_log = cls._load_session_log(session_id)
            
            # Update metadata
            session_log["lastUpdated"] = datetime.now().isoformat()
            session_log["totalTurns"] += 1
            session_log["scamDetected"] = session_log["scamDetected"] or scam_detected
            
            # Add turn
            turn_data = {
                "turn": session_log["totalTurns"],
                "timestamp": datetime.now().isoformat(),
                "scammerMessage": scammer_message,
                "honeypotReply": honeypot_reply,
                "detected": scam_detected,
                "action": action,
                "intelligence": intelligence,
                "notes": notes
            }
            session_log["turns"].append(turn_data)
            
            # Accumulate final intelligence (deduplicated)
            for key, values in intelligence.items():
                if key in session_log["finalIntelligence"]:
                    existing = set(session_log["finalIntelligence"][key])
                    existing.update(values)
                    session_log["finalIntelligence"][key] = sorted(list(existing))
            
            # Write to file
            log_path = cls._get_log_path(session_id)
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(session_log, f, indent=2, ensure_ascii=False)
            
            print(f"[SessionLogger] Logged turn {session_log['totalTurns']} for session {session_id}")
            
        except Exception as e:
            print(f"[SessionLogger] Error logging session {session_id}: {e}")
    
    @classmethod
    def get_all_sessions(cls) -> List[str]:
        """Get list of all logged session IDs."""
        cls._ensure_log_dir()
        session_files = cls.LOG_DIR.glob("session_*.json")
        return [f.stem.replace("session_", "") for f in session_files]
    
    @classmethod
    def get_session_summary(cls, session_id: str) -> Dict[str, Any]:
        """Get summary of a session."""
        log_path = cls._get_log_path(session_id)
        if not log_path.exists():
            return None
        
        with open(log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "sessionId": data["sessionId"],
            "started": data["started"],
            "totalTurns": data["totalTurns"],
            "scamDetected": data["scamDetected"],
            "intelligenceCount": sum(len(v) for v in data["finalIntelligence"].values())
        }
