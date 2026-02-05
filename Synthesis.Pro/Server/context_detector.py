"""
Context Detector
Detects when user references previous work and offers relevant context proactively.

Philosophy: Make context feel helpful and timely, not intrusive.
Only offer when there's clear signal the user needs it.
"""

import re
from typing import Dict, List, Optional
from context_preview import ContextPreviewService


class ContextDetector:
    """Detect when user needs context about previous work"""

    # Patterns indicating user is referencing previous work
    REFERENCE_PATTERNS = [
        r'\b(continue|last time|we discussed|working on|previously)\b',
        r'\b(remember|recall|earlier|before)\b',
        r'\b(where were we|what were we|status on)\b'
    ]

    # Project/feature name patterns
    PROJECT_PATTERNS = [
        r'\b(NightBlade|Synthesis\.Pro|project|feature)\b',
        r'\b(bug|issue|error|problem)\b',
        r'\b(implement|build|create|design)\b'
    ]

    def __init__(self, rag_engine):
        self.rag = rag_engine
        self.min_confidence = 0.6  # Threshold for offering context

    def detect_context_need(self, user_message: str) -> Dict:
        """
        Analyze user message to detect if they're referencing previous work.

        Returns dict with:
        - has_context: bool
        - context: Optional[str] formatted suggestion
        - confidence: float (0-1)
        - results: Optional[List] raw search results if found
        """
        # Check for reference patterns
        has_reference = any(
            re.search(pattern, user_message, re.IGNORECASE)
            for pattern in self.REFERENCE_PATTERNS
        )

        has_project = any(
            re.search(pattern, user_message, re.IGNORECASE)
            for pattern in self.PROJECT_PATTERNS
        )

        if not (has_reference or has_project):
            return {'has_context': False, 'confidence': 0.0}

        # Search for relevant context
        relevant = self.rag.search(query=user_message, top_k=3)

        if not relevant or len(relevant) == 0:
            return {'has_context': False, 'confidence': 0.0}

        # Calculate confidence based on relevance
        confidence = self._calculate_confidence(user_message, relevant)

        if confidence < self.min_confidence:
            return {'has_context': False, 'confidence': confidence}

        # Format context suggestion
        context_text = self._format_suggestion(relevant)

        return {
            'has_context': True,
            'context': context_text,
            'confidence': confidence,
            'results': relevant
        }

    def _calculate_confidence(self, user_message: str, results: List[Dict]) -> float:
        """
        Calculate confidence that these results match user's intent.

        Higher confidence = more likely user will find this helpful.
        """
        if not results:
            return 0.0

        # Start with base similarity score from top result
        top_score = results[0].get('similarity', 0.0)

        # Boost confidence if message explicitly asks for context
        explicit_ask = any(
            keyword in user_message.lower()
            for keyword in ['continue', 'status', 'where were we', 'last time']
        )

        if explicit_ask:
            top_score *= 1.3  # 30% boost for explicit asks

        # Reduce confidence if message is very short (might be vague)
        if len(user_message.split()) < 5:
            top_score *= 0.8

        return min(top_score, 1.0)  # Cap at 1.0

    def _format_suggestion(self, results: List[Dict]) -> str:
        """Format context as natural suggestion, not retrieval dump"""

        if not results:
            return ""

        # Use top result as primary context
        top = results[0]
        text = top.get('text', '')

        # Truncate if too long
        if len(text) > 200:
            text = text[:200] + "..."

        # Format as helpful suggestion
        if len(results) == 1:
            return f"From your previous work: \"{text}\""
        else:
            additional = len(results) - 1
            return f"From your previous work: \"{text}\"\n\n(+{additional} more related notes available)"

    def extract_project_name(self, user_message: str) -> Optional[str]:
        """
        Extract specific project name if mentioned.

        Useful for targeted context retrieval.
        """
        known_projects = ['NightBlade', 'Synthesis.Pro', 'Synthesis', 'Unity']

        for project in known_projects:
            if project.lower() in user_message.lower():
                return project

        return None


if __name__ == "__main__":
    # Test context detection
    import sys
    import os
    from pathlib import Path

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RAG'))
    from rag_engine import RAGEngine

    db_path = Path(__file__).parent.parent / "KnowledgeBase" / "databases" / "public_knowledge.db"

    if db_path.exists():
        rag = RAGEngine(str(db_path))
        detector = ContextDetector(rag)

        # Test messages
        test_messages = [
            "continue working on NightBlade",
            "what's the status on the RAG system?",
            "hello",  # Should not trigger
            "implement new feature"  # Might trigger depending on content
        ]

        for msg in test_messages:
            print(f"\nMessage: \"{msg}\"")
            result = detector.detect_context_need(msg)
            print(f"Has context: {result['has_context']}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
            if result['has_context']:
                print(f"Context: {result['context']}")
            print("-" * 60)
    else:
        print(f"Database not found at {db_path}")
