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

    def _query_ollama(self, messages: List[Dict[str, str]], json_format: bool = False) -> str:
        import urllib.request
        import json
        from config.settings import settings

        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
        if json_format:
            payload["format"] = "json"

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error querying Ollama directly: {e}")
            raise e

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

        # Stage 1: Heuristic check for quick greetings/help
        has_digits = any(char.isdigit() for char in message)
        clean_msg = message.strip("?!. \t\n\r").lower()
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "yo", "help", "thanks", "thank you"}
        
        if clean_msg in greetings or len(clean_msg) < 5 or not has_digits:
            is_deep = False
        else:
            # Stage 2: LLM classifier call
            system_prompt = (
                "You are a routing assistant. Classify the user query into exactly one of two categories: 'DEEP' or 'SIMPLE'.\n"
                "Choose 'DEEP' ONLY if the user provides specific numerical details (like income, expenses, loan amounts, interest rates, or specific SIP investment amounts) and wants calculations or structured planning.\n"
                "Choose 'SIMPLE' if the query is a greeting, general conversational follow-up, or general question without numbers.\n"
                "Reply with exactly one word: 'DEEP' or 'SIMPLE'. Do not write anything else."
            )
            try:
                clf_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {message}"}
                ]
                decision = self._query_ollama(clf_messages).upper()
                is_deep = "DEEP" in decision
                logger.info(f"Classifier decision: {decision} (is_deep={is_deep})")
            except Exception as e:
                logger.warning(f"Classification failed: {e}. Defaulting to DEEP workflow.")
                is_deep = True

        try:
            if not is_deep:
                logger.info("Executing SIMPLE fast-path query")
                system_prompt = (
                    "You are a helpful, friendly Personal Finance Advisor. "
                    "Answer the user's query directly, concisely, and friendly. Do not perform any deep multi-agent planning "
                    "simulation or output JSON. Just respond in clear natural language."
                )
                ollama_messages = [{"role": "system", "content": system_prompt}]
                for msg in history:
                    ollama_messages.append({"role": msg["role"], "content": msg["content"]})
                
                response = self._query_ollama(ollama_messages)
            else:
                # Delegate directly to sequential CrewAI workflow
                response = self.workflow.run(context_query)
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            # Remove the failed user message so it doesn't corrupt history context
            if self._sessions[session_id]:
                self._sessions[session_id].pop()
            raise e
            
        self.add_message(session_id, "assistant", response)
        return response

