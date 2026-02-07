"""
Curiosity Trigger
Detects AI uncertainty and offers helpful context proactively.

Philosophy: Context feels most natural when it answers questions you didn't
know you needed to ask. When AI expresses uncertainty, offer relevant knowledge.
"""

from typing import Dict, List, Optional
import re


class CuriosityTrigger:
    """Detect AI uncertainty and offer context that might help"""

    # Phrases indicating AI doesn't have needed context
    UNCERTAINTY_PHRASES = [
        "I don't have context",
        "I'm not sure what",
        "I don't know about",
        "Could you provide more",
        "Can you explain",
        "What is",
        "I'm not familiar with",
        "I don't see",
        "I'm not aware of",
        "I haven't seen",
        "without more context",
        "need more information"
    ]

    # Phrases indicating AI is making assumptions (yellow flag)
    ASSUMPTION_PHRASES = [
        "I assume",
        "I'm guessing",
        "It seems like",
        "Probably",
        "It appears",
        "Based on what I can see"
    ]

    def __init__(self, rag_engine, min_confidence: float = 0.7):
        self.rag = rag_engine
        self.min_confidence = min_confidence

    def detect_uncertainty(self, ai_response: str) -> Dict[str, any]:
        """
        Detect if AI response shows uncertainty or lack of context.

        Returns:
        - is_uncertain: bool
        - uncertainty_type: 'missing_context' | 'making_assumptions' | None
        - topic: Optional[str] what the AI is uncertain about
        """
        lower_response = ai_response.lower()

        # Check for explicit uncertainty
        for phrase in self.UNCERTAINTY_PHRASES:
            if phrase.lower() in lower_response:
                topic = self._extract_topic_after_phrase(ai_response, phrase)
                return {
                    'is_uncertain': True,
                    'uncertainty_type': 'missing_context',
                    'topic': topic,
                    'phrase_matched': phrase
                }

        # Check for assumptions (softer signal)
        for phrase in self.ASSUMPTION_PHRASES:
            if phrase.lower() in lower_response:
                topic = self._extract_topic_after_phrase(ai_response, phrase)
                return {
                    'is_uncertain': True,
                    'uncertainty_type': 'making_assumptions',
                    'topic': topic,
                    'phrase_matched': phrase
                }

        return {
            'is_uncertain': False,
            'uncertainty_type': None,
            'topic': None
        }

    def offer_context(self, ai_response: str, user_message: str) -> Optional[Dict]:
        """
        Proactively offer relevant context when AI shows uncertainty.

        Returns None if no uncertainty detected or no helpful context found.
        Returns formatted context suggestion if relevant info available.
        """
        uncertainty = self.detect_uncertainty(ai_response)

        if not uncertainty['is_uncertain']:
            return None

        # Try to identify what topic the AI is uncertain about
        topic = uncertainty.get('topic')

        if not topic:
            # Fall back to user message as search query
            topic = user_message

        # Search for relevant context
        results = self.rag.search(query=topic, top_k=3)

        if not results or len(results) == 0:
            return None

        # Check if results are actually relevant
        top_similarity = results[0].get('similarity', 0.0)

        if top_similarity < self.min_confidence:
            return None  # Not confident this helps

        # Format as helpful context offer
        return {
            'has_context': True,
            'uncertainty_type': uncertainty['uncertainty_type'],
            'topic': topic,
            'suggestion': self._format_context_offer(results, uncertainty),
            'results': results
        }

    def _extract_topic_after_phrase(self, text: str, phrase: str) -> Optional[str]:
        """
        Extract the topic that comes after an uncertainty phrase.

        Example: "I don't know about the RAG system" -> "RAG system"
        """
        # Find the phrase in text (case-insensitive)
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        match = pattern.search(text)

        if not match:
            return None

        # Extract text after the phrase
        after_phrase = text[match.end():].strip()

        # Extract first meaningful chunk (usually up to period/comma/question mark)
        topic_match = re.match(r'^([^.,!?]+)', after_phrase)

        if topic_match:
            topic = topic_match.group(1).strip()
            # Clean up common words
            topic = re.sub(r'\b(the|a|an|this|that|these|those)\b', '', topic, flags=re.IGNORECASE)
            return topic.strip()

        return None

    def _format_context_offer(self, results: List[Dict], uncertainty: Dict) -> str:
        """Format context as natural offer, not forceful injection"""

        uncertainty_type = uncertainty.get('uncertainty_type')
        topic = uncertainty.get('topic', 'this')

        # Choose framing based on uncertainty type
        if uncertainty_type == 'missing_context':
            intro = f"I found some relevant context about {topic}:"
        else:  # making_assumptions
            intro = f"For better accuracy, here's what I have about {topic}:"

        # Format top result
        top = results[0]
        text = top.get('text', '')

        if len(text) > 250:
            text = text[:250] + "..."

        suggestion = f"{intro}\n\n\"{text}\""

        # Add note if more context available
        if len(results) > 1:
            suggestion += f"\n\n({len(results) - 1} more related notes available)"

        return suggestion

    def should_suggest_rag_exploration(self, conversation_history: List[str]) -> bool:
        """
        Detect if AI keeps hitting uncertainty - might benefit from exploring RAG.

        This is the "meta" suggestion: not specific context, but suggestion to
        explore the knowledge base itself.
        """
        if len(conversation_history) < 3:
            return False

        # Check recent messages for repeated uncertainty
        recent_uncertain_count = 0

        for message in conversation_history[-5:]:  # Last 5 AI responses
            if self.detect_uncertainty(message)['is_uncertain']:
                recent_uncertain_count += 1

        # If 3+ uncertain responses in last 5 messages, suggest exploration
        return recent_uncertain_count >= 3


if __name__ == "__main__":
    # Test curiosity trigger
    import sys
    import os
    from pathlib import Path

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RAG'))
    from rag_engine_lite import SynthesisRAG as RAGEngine

    db_path = Path(__file__).parent.parent / "KnowledgeBase" / "databases" / "public_knowledge.db"

    if db_path.exists():
        rag = RAGEngine(str(db_path))
        trigger = CuriosityTrigger(rag)

        # Test AI responses
        test_responses = [
            "I don't have context about the NightBlade project structure.",
            "I'm not sure what the RAG system architecture looks like.",
            "I assume you want me to implement this feature.",
            "This looks good to me!"  # Should not trigger
        ]

        test_user_message = "Can you help with the project?"

        for response in test_responses:
            print(f"\nAI Response: \"{response}\"")
            uncertainty = trigger.detect_uncertainty(response)
            print(f"Is uncertain: {uncertainty['is_uncertain']}")

            if uncertainty['is_uncertain']:
                print(f"Type: {uncertainty['uncertainty_type']}")
                print(f"Topic: {uncertainty['topic']}")

                offer = trigger.offer_context(response, test_user_message)
                if offer:
                    print(f"\nContext offer:\n{offer['suggestion']}")
                else:
                    print("No relevant context found")

            print("-" * 60)
    else:
        print(f"Database not found at {db_path}")
