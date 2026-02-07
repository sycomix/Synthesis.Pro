"""
Context Preview Service
Generates natural context for new AI instances without feeling forced.

Philosophy: Enable, don't force. Context should feel like helpful orientation,
not mandatory retrieval.
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add rag_engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RAG'))
from rag_engine_lite import SynthesisRAG as RAGEngine  # NEW: Using lightweight RAG


class ContextPreviewService:
    """Generate welcoming context previews for new AI sessions"""

    def __init__(self, rag_engine: RAGEngine, user_id: str):
        self.rag = rag_engine
        self.user_id = user_id
        self.max_preview_items = 5

    def generate_session_preview(self, include_time_filter: bool = True) -> Optional[str]:
        """
        Generate natural context preview for session startup.

        Returns None if no relevant context exists (clean slate is fine).
        Returns natural language summary if recent work detected.
        """
        # Search for recent activity
        query = f"recent work projects activity user:{self.user_id}"

        recent_results = self.rag.search(query=query, top_k=self.max_preview_items)

        if not recent_results or len(recent_results) == 0:
            return None  # No context = fresh start, and that's okay

        # Extract meaningful information
        projects = self._extract_project_names(recent_results)
        topics = self._extract_topics(recent_results)

        if not projects and not topics:
            return None

        # Format as natural orientation, not retrieval report
        return self._format_preview(projects, topics, recent_results)

    def _extract_project_names(self, results: List[Dict]) -> List[str]:
        """Extract project names from search results"""
        projects = set()
        project_keywords = ['NightBlade', 'Synthesis.Pro', 'Unity', 'RAG', 'Asset Store']

        for result in results:
            text = result.get('text', '')
            for keyword in project_keywords:
                if keyword.lower() in text.lower():
                    projects.add(keyword)

        return list(projects)[:3]  # Max 3 projects in preview

    def _extract_topics(self, results: List[Dict]) -> List[str]:
        """Extract key topics/activities from search results"""
        topics = []

        # Common development activities
        activity_patterns = [
            ('testing', ['test', 'verify', 'validation']),
            ('documentation', ['docs', 'documentation', 'guide']),
            ('implementation', ['implement', 'build', 'create']),
            ('debugging', ['debug', 'fix', 'error', 'bug']),
            ('design', ['design', 'architecture', 'plan'])
        ]

        for result in results[:3]:  # Check top 3 results
            text = result.get('text', '').lower()
            for topic_name, keywords in activity_patterns:
                if any(keyword in text for keyword in keywords):
                    if topic_name not in topics:
                        topics.append(topic_name)

        return topics[:3]  # Max 3 topics

    def _format_preview(self, projects: List[str], topics: List[str],
                       results: List[Dict]) -> str:
        """Format as welcoming context, not forced retrieval"""

        # Build natural language summary
        parts = []

        if projects:
            if len(projects) == 1:
                parts.append(f"You've been working on {projects[0]}")
            else:
                parts.append(f"You've been working on {', '.join(projects[:-1])} and {projects[-1]}")

        if topics:
            topic_phrase = ', '.join(topics)
            parts.append(f"Recent focus: {topic_phrase}")

        # Add most relevant recent item as example
        if results and len(results) > 0:
            recent = results[0].get('text', '')
            if len(recent) > 150:
                recent = recent[:150] + "..."
            parts.append(f"\nLast note: \"{recent}\"")

        preview = '. '.join(parts) if len(parts) > 1 else parts[0] if parts else ""

        # Add helpful framing
        if preview:
            preview = f"Welcome back! {preview}\n\nHow can I help you continue this work?"

        return preview

    def get_project_context(self, project_name: str, n: int = 3) -> List[Dict]:
        """
        Get specific context about a project when user mentions it.

        This is for when user says "continue working on X" - we can offer
        relevant context without them asking explicitly.
        """
        query = f"{project_name} recent progress status"
        return self.rag.search(query=query, top_k=n)


if __name__ == "__main__":
    # Test the preview service
    from pathlib import Path

    # Use public database for testing
    db_path = Path(__file__).parent.parent / "KnowledgeBase" / "databases" / "public_knowledge.db"

    if db_path.exists():
        rag = RAGEngine(str(db_path))
        preview_service = ContextPreviewService(rag, "test_user")

        preview = preview_service.generate_session_preview()

        if preview:
            print("Generated Preview:")
            print("=" * 60)
            print(preview)
            print("=" * 60)
        else:
            print("No recent context found - fresh start!")
    else:
        print(f"Database not found at {db_path}")
        print("Run first-time setup in Unity first.")
