"""
Session Manager for conversation state management
Supports in-memory and Redis storage
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import settings
from app.models.session import SessionData

# In-memory storage
_sessions: Dict[str, SessionData] = {}


class SessionManager:
    """Manages conversation sessions"""
    
    def __init__(self):
        """Initialize session manager"""
        self.use_redis = settings.USE_REDIS
        self.redis_client = None
        
        if self.use_redis:
            try:
                import redis
                self.redis_client = redis.from_url(settings.REDIS_URL)
                print("✓ Redis session store initialized")
            except Exception as e:
                print(f"✗ Redis initialization failed: {e}")
                print("→ Falling back to in-memory storage")
                self.use_redis = False
        else:
            print("✓ In-memory session store initialized")
    
    def create_session(self, session_id: str) -> SessionData:
        """Create a new session"""
        session = SessionData(
            session_id=session_id,
            status="active",
            scam_detected=False,
            turn_count=0,
            conversation_history=[],
            extracted_intel={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve a session"""
        if self.use_redis and self.redis_client:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                if data:
                    session_dict = json.loads(data)
                    return SessionData(**session_dict)
            except Exception as e:
                print(f"✗ Redis get error: {e}")
        
        return _sessions.get(session_id)
    
    def update_session(self, session: SessionData):
        """Update an existing session"""
        session.updated_at = datetime.now()
        self._save_session(session)
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(f"session:{session_id}")
            except Exception as e:
                print(f"✗ Redis delete error: {e}")
        
        if session_id in _sessions:
            del _sessions[session_id]
    
    def _save_session(self, session: SessionData):
        """Save session to storage"""
        if self.use_redis and self.redis_client:
            try:
                session_dict = session.dict()
                # Convert datetime to string for JSON
                session_dict['created_at'] = session_dict['created_at'].isoformat()
                session_dict['updated_at'] = session_dict['updated_at'].isoformat()
                
                self.redis_client.setex(
                    f"session:{session.session_id}",
                    settings.SESSION_TIMEOUT,
                    json.dumps(session_dict)
                )
            except Exception as e:
                print(f"✗ Redis save error: {e}")
        
        # Always save to in-memory as backup
        _sessions[session.session_id] = session


# Global instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get or create global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
