from typing import Dict, Optional, Any
from app.models.session import SessionData # I'll define this next

# In-memory session store for development
_sessions: Dict[str, Any] = {}

class SessionManager:
    @staticmethod
    def get_or_create_session(session_id: str) -> SessionData:
        if session_id not in _sessions:
            _sessions[session_id] = SessionData(sessionId=session_id)
        return _sessions[session_id]

    @staticmethod
    def update_session(session_id: str, **kwargs):
        if session_id in _sessions:
            session = _sessions[session_id]
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
