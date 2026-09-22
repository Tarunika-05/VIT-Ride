from typing import Dict, List, Optional

class ConversationMemory:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        """Append a message to the specified session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
            
        self._sessions[session_id].append({
            "role": role,
            "content": content
        })
        
        # Enforce sliding window capacity
        if len(self._sessions[session_id]) > self.max_history:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve message history for a session."""
        return self._sessions.get(session_id, [])

    def clear(self, session_id: str):
        """Clear history for a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def list_sessions(self) -> List[str]:
        """Return list of active session IDs."""
        return list(self._sessions.keys())

memory_manager = ConversationMemory()
