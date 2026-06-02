import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # In-memory session history storage (session_id -> list of message dicts)
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        
        # Instantiate workflow dynamically to prevent circular dependencies
        from workflows.finance_workflow import FinanceWorkflow
        self.workflow = FinanceWorkflow()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve chat history for a given session.
        """
        if not session_id:
            return []
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to the session's chat history.
        """
        if not session_id:
            return
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})
        
        # Limit history size to prevent context overflow (keep last 10 exchanges / 20 messages)
        if len(self._sessions[session_id]) > 20:
            self._sessions[session_id] = self._sessions[session_id][-20:]

    def clear_session(self, session_id: str):
        """
        Clear session history.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

    def chat(self, session_id: str, message: str) -> str:
        """
        Respond to user queries by delegating directly to the CrewAI workflow.
        """
        logger.info(f"Processing chat request for session: {session_id}")
        
        # Save user query to session memory
        self.add_message(session_id, "user", message)
        
        # Format query context with session memory history
        history = self.get_history(session_id)
        context_query = ""
        if len(history) > 1:
            context_query += "Previous conversation context:\n"
            for msg in history[:-1]:
                speaker = "User" if msg["role"] == "user" else "Advisor"
                context_query += f"{speaker}: {msg['content']}\n"
            context_query += f"\nAnswer the new user query: '{message}'"
        else:
            context_query = message
            
        try:
            # Delegate directly to sequential CrewAI workflow
            response = self.workflow.run(context_query)
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            # Remove the failed user message so it doesn't corrupt history context
            if self._sessions[session_id]:
                self._sessions[session_id].pop()
            raise e
            
        self.add_message(session_id, "assistant", response)
        return response
