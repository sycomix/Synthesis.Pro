"""
Synthesis.Pro Conversation History Tracker
Stores conversation history in the PRIVATE RAG database
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class ConversationTracker:
    """
    Tracks conversation history in the private RAG database.

    This enables AI to maintain context across sessions, learn from
    past interactions, and build a genuine relationship with the user.
    """

    def __init__(self, rag_engine):
        """
        Initialize conversation tracker.

        Args:
            rag_engine: SynthesisRAG instance with dual database support
        """
        self.rag = rag_engine
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_message(
        self,
        role: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a conversation message to the private database.

        Args:
            role: "user" or "assistant"
            message: The message content
            context: Optional context (scene, file, etc.)
            metadata: Optional metadata (tokens, model, etc.)

        Returns:
            Success status
        """
        try:
            timestamp = datetime.now().isoformat()

            # Format conversation entry
            entry = {
                "timestamp": timestamp,
                "session_id": self.session_id,
                "role": role,
                "message": message
            }

            if context:
                entry["context"] = context

            if metadata:
                entry["metadata"] = metadata

            # Create searchable text for RAG
            formatted_text = self._format_for_rag(entry)

            # Store in PRIVATE database
            return self.rag.add_text(formatted_text, private=True)
        except Exception as e:
            print(f"Error adding conversation message: {e}")
            return False

    def add_user_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a user message to conversation history.

        Args:
            message: User's message
            context: Optional context information

        Returns:
            Success status
        """
        return self.add_message("user", message, context)

    def add_assistant_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an assistant message to conversation history.

        Args:
            message: Assistant's response
            context: Optional context information
            metadata: Optional metadata (model, tokens, etc.)

        Returns:
            Success status
        """
        return self.add_message("assistant", message, context, metadata)

    def add_exchange(
        self,
        user_message: str,
        assistant_message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a complete exchange (user + assistant) to history.

        Args:
            user_message: User's message
            assistant_message: Assistant's response
            context: Optional context
            metadata: Optional metadata

        Returns:
            Success status
        """
        success = self.add_user_message(user_message, context)
        success = success and self.add_assistant_message(
            assistant_message,
            context,
            metadata
        )
        return success

    def search_conversation_history(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Search through conversation history.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant conversation entries
        """
        try:
            # Search only in private database
            results = self.rag.search(query, top_k=top_k, scope="private")

            # Filter for conversation entries
            conversations = []
            for result in results:
                if result['text'].startswith('[CONVERSATION]'):
                    conversations.append(result)

            return conversations
        except Exception as e:
            print(f"Error searching conversation history: {e}")
            return []

    def get_recent_context(self, limit: int = 5) -> str:
        """
        Get recent conversation context for AI to reference.

        Args:
            limit: Number of recent messages to retrieve

        Returns:
            Formatted context string
        """
        # Search for recent conversations in this session
        results = self.search_conversation_history(
            f"session:{self.session_id}",
            top_k=limit
        )

        if not results:
            return "No recent conversation history."

        # Format for AI consumption
        context_parts = []
        for result in results:
            context_parts.append(result['text'])

        return "\n".join(context_parts)

    def add_learning(
        self,
        observation: str,
        category: str = "general"
    ) -> bool:
        """
        Add a learning or observation to private database.

        Use this when AI notices patterns or learns something
        about the user's preferences or working style.

        Args:
            observation: What was learned
            category: Category (preference, pattern, style, etc.)

        Returns:
            Success status
        """
        try:
            formatted = f"[LEARNING:{category}] Session: {self.session_id} | {observation}"
            return self.rag.add_text(formatted, private=True)
        except Exception as e:
            print(f"Error adding learning: {e}")
            return False

    def add_decision(
        self,
        decision: str,
        rationale: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a decision made during the conversation.

        Helps track why certain choices were made for future reference.

        Args:
            decision: The decision made
            rationale: Why this decision was made
            context: Optional context

        Returns:
            Success status
        """
        try:
            formatted = (
                f"[DECISION] Session: {self.session_id}\n"
                f"Decision: {decision}\n"
                f"Rationale: {rationale}"
            )

            if context:
                formatted += f"\nContext: {json.dumps(context)}"

            return self.rag.add_text(formatted, private=True)
        except Exception as e:
            print(f"Error adding decision: {e}")
            return False

    def _format_for_rag(self, entry: Dict) -> str:
        """
        Format conversation entry for RAG storage.

        Args:
            entry: Conversation entry dict

        Returns:
            Formatted string for RAG indexing
        """
        formatted = (
            f"[CONVERSATION] "
            f"Session: {entry['session_id']} | "
            f"Time: {entry['timestamp']} | "
            f"Role: {entry['role']}\n"
            f"Message: {entry['message']}"
        )

        if 'context' in entry:
            formatted += f"\nContext: {json.dumps(entry['context'])}"

        if 'metadata' in entry:
            formatted += f"\nMetadata: {json.dumps(entry['metadata'])}"

        return formatted

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session.

        Returns:
            Summary dictionary with session stats
        """
        try:
            results = self.search_conversation_history(
                f"session:{self.session_id}",
                top_k=1000  # Get all from this session
            )

            user_messages = [r for r in results if '"role": "user"' in r['text']]
            assistant_messages = [r for r in results if '"role": "assistant"' in r['text']]

            return {
                "session_id": self.session_id,
                "total_exchanges": len(user_messages) + len(assistant_messages),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "start_time": self.session_id,
            }
        except Exception as e:
            print(f"Error getting session summary: {e}")
            return {
                "session_id": self.session_id,
                "error": str(e)
            }


if __name__ == "__main__":
    # Example usage
    from rag_engine_lite import SynthesisRAG

    print("=" * 60)
    print("Synthesis.Pro Conversation Tracker Demo")
    print("=" * 60)

    # Initialize RAG with dual database
    rag = SynthesisRAG(
        database="test_public.db",
        private_database="test_private.db",
        embedding_provider="local"
    )

    # Create conversation tracker
    tracker = ConversationTracker(rag)

    print(f"\n📝 Session ID: {tracker.session_id}")

    # Add some conversation exchanges
    print("\n💬 Adding conversation history...")
    tracker.add_exchange(
        user_message="How do I instantiate a prefab in Unity?",
        assistant_message="You can use Instantiate(prefab, position, rotation)",
        context={"scene": "MainScene", "file": "GameManager.cs"}
    )

    tracker.add_exchange(
        user_message="What's the difference between Awake and Start?",
        assistant_message="Awake is called when the script instance is loaded, Start is called before the first frame update",
        context={"scene": "MainScene"}
    )

    # Record a learning
    print("\n🧠 Recording learning...")
    tracker.add_learning(
        "User asks detailed questions about Unity lifecycle methods",
        category="preference"
    )

    # Record a decision
    print("\n📋 Recording decision...")
    tracker.add_decision(
        decision="Use coroutines instead of async/await for this task",
        rationale="Better integration with Unity's lifecycle",
        context={"scene": "MainScene"}
    )

    # Search conversation history
    print("\n🔍 Searching conversation history...")
    results = tracker.search_conversation_history("prefab", top_k=3)
    print(f"Found {len(results)} relevant conversations:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. [{result['source']}] Score: {result['score']}")
        print(f"   {result['text'][:100]}...")

    # Get session summary
    print("\n📊 Session Summary:")
    summary = tracker.get_session_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("✅ Conversation tracking working!")
    print("   All history stored in PRIVATE database")
    print("=" * 60)
