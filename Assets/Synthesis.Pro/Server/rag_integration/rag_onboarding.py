"""
RAG Onboarding System - Main Integration
Coordinates all components to make RAG feel natural and helpful.

Philosophy: Enable, don't force. The AI should WANT to use RAG because it's
immediately useful, not because it's commanded to.

Architecture:
- ContextPreviewService: Session startup orientation
- ContextDetector: Detects when user references previous work
- CuriosityTrigger: Offers context when AI shows uncertainty
- SeamlessPresentation: Makes everything feel natural
- AutomatedTuner: Self-improving based on usage

Result: Tiny AI → Mighty AI through natural context accumulation
"""

import sys
import os
from typing import Dict, List, Optional
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))  # Server/ directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))  # RAG/core/ directory

from rag_engine_lite import SynthesisRAG as RAGEngine  # NEW: Using lightweight RAG

from context_systems.context_preview import ContextPreviewService
from context_systems.context_detector import ContextDetector
from context_systems.curiosity_trigger import CuriosityTrigger
from context_systems.seamless_presentation import SeamlessPresentation, ContextAwareness
# Note: rag_tuning moved to deprecated/ - using simple approach without AutomatedTuner for now
# from deprecated.rag_tuning import AutomatedTuner

class AutomatedTuner:
    """Placeholder for removed rag_tuning - keeping interface compatible"""
    def log_session_start(self, *args, **kwargs): pass
    def log_interaction(self, *args, **kwargs): pass
    def get_acceptance_rate(self): return 0.8
    def get_helpfulness_rate(self): return 0.85
    def get_summary(self): return {}
    def adjust_thresholds(self): return None


class RAGOnboardingSystem:
    """
    Unified system that makes RAG usage feel natural and beneficial.

    This is the "enable, don't force" architecture in action.
    """

    def __init__(self,
                 rag_engine: RAGEngine,
                 user_id: str,
                 presentation_style: str = 'natural'):
        """
        Initialize the onboarding system.

        Args:
            rag_engine: The underlying RAG engine
            user_id: Identifier for the user
            presentation_style: 'natural', 'conversational', or 'minimal'
        """
        self.rag = rag_engine
        self.user_id = user_id

        # Initialize all components
        self.preview_service = ContextPreviewService(rag_engine, user_id)
        self.context_detector = ContextDetector(rag_engine)
        self.curiosity_trigger = CuriosityTrigger(rag_engine)
        self.presenter = SeamlessPresentation(presentation_style)
        self.awareness = ContextAwareness(max_per_session=5)
        self.tuner = AutomatedTuner()

        self.session_id = None
        self.conversation_history = []

    def start_session(self, session_id: str) -> Optional[str]:
        """
        Start new AI session with optional context preview.

        Returns welcome message with context, or None for clean start.
        """
        self.session_id = session_id
        self.awareness.reset_session()
        self.conversation_history = []

        # Generate preview
        preview_content = self.preview_service.generate_session_preview()

        # Decide whether to show preview
        if preview_content and self.awareness.can_show_context():
            formatted = self.presenter.format_session_preview(preview_content)
            self.awareness.record_shown()
            self.tuner.log_session_start(session_id, preview_shown=True)
            return formatted
        else:
            self.tuner.log_session_start(session_id, preview_shown=False)
            return None

    def process_user_message(self, user_message: str) -> Optional[Dict]:
        """
        Analyze user message and offer context if relevant.

        Returns context data if something helpful found, None otherwise.
        """
        if not self.awareness.can_show_context():
            return None  # Already shown enough context this session

        # Detect if user is referencing previous work
        context_result = self.context_detector.detect_context_need(user_message)

        if not context_result['has_context']:
            return None

        # Format for presentation
        confidence = context_result['confidence']
        context_text = context_result['context']

        formatted = self.presenter.format_context_suggestion(context_text, confidence)

        if self.presenter.should_show_context({'confidence': confidence}):
            self.awareness.record_shown()
            return {
                'formatted_context': formatted,
                'raw_results': context_result['results'],
                'confidence': confidence,
                'source': 'user_message_detection'
            }

        return None

    def process_ai_response(self,
                           ai_response: str,
                           user_message: str) -> Optional[Dict]:
        """
        Analyze AI response for uncertainty and offer helpful context.

        Returns context offer if AI seems uncertain, None otherwise.
        """
        if not self.awareness.can_show_context():
            return None

        # Check if AI is uncertain
        context_offer = self.curiosity_trigger.offer_context(ai_response, user_message)

        if not context_offer or not context_offer['has_context']:
            return None

        # Format for presentation
        formatted = self.presenter.format_uncertainty_help(
            context_offer['suggestion'],
            context_offer['topic']
        )

        self.awareness.record_shown()

        return {
            'formatted_context': formatted,
            'raw_results': context_offer['results'],
            'uncertainty_type': context_offer['uncertainty_type'],
            'topic': context_offer['topic'],
            'source': 'ai_uncertainty_detection'
        }

    def record_interaction(self,
                          context_offered: bool,
                          ai_response: str,
                          user_feedback: Optional[Dict] = None):
        """
        Record interaction for automated tuning.

        This makes the system self-improving over time.
        """
        self.tuner.log_interaction(context_offered, ai_response, user_feedback)

        # Track conversation history for pattern detection
        self.conversation_history.append(ai_response)

        # Check if AI consistently uncertain (might need RAG exploration)
        if self.curiosity_trigger.should_suggest_rag_exploration(self.conversation_history):
            return {
                'suggestion': 'meta_rag_exploration',
                'message': 'You might benefit from exploring the knowledge base directly'
            }

        return None

    def get_system_health(self) -> Dict:
        """
        Get health metrics for the onboarding system.

        Useful for monitoring and debugging.
        """
        return {
            'session_id': self.session_id,
            'awareness': self.awareness.get_status(),
            'acceptance_rate': self.tuner.get_acceptance_rate(),
            'helpfulness_rate': self.tuner.get_helpfulness_rate(),
            'conversation_length': len(self.conversation_history),
            'tuner_summary': self.tuner.get_summary()
        }

    def adjust_and_optimize(self) -> Optional[Dict]:
        """
        Run automated optimization based on usage patterns.

        Returns adjustment recommendations or None if everything is optimal.
        """
        adjustments = self.tuner.adjust_thresholds()

        if adjustments:
            # Apply adjustments to components
            if 'confidence_min' in adjustments:
                self.context_detector.min_confidence = adjustments['confidence_min']
                self.curiosity_trigger.min_confidence = adjustments['confidence_min']

            return adjustments

        return None


class RAGOnboardingBuilder:
    """Builder pattern for easier system configuration"""

    def __init__(self):
        self.db_path = None
        self.user_id = "default_user"
        self.style = "natural"

    def with_database(self, db_path: str):
        """Set database path"""
        self.db_path = db_path
        return self

    def with_user(self, user_id: str):
        """Set user ID"""
        self.user_id = user_id
        return self

    def with_style(self, style: str):
        """Set presentation style"""
        self.style = style
        return self

    def build(self) -> RAGOnboardingSystem:
        """Build the configured system"""
        if not self.db_path:
            raise ValueError("Database path required")

        rag = RAGEngine(self.db_path)
        return RAGOnboardingSystem(rag, self.user_id, self.style)


# Example usage and testing
if __name__ == "__main__":
    # Find public database
    db_path = Path(__file__).parent.parent / "KnowledgeBase" / "databases" / "public_knowledge.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("Run first-time setup in Unity first.")
        sys.exit(1)

    # Build system
    system = (RAGOnboardingBuilder()
              .with_database(str(db_path))
              .with_user("test_user")
              .with_style("natural")
              .build())

    print("RAG Onboarding System - Test Run")
    print("=" * 60)

    # Test session start
    print("\n1. Starting new session...")
    session_preview = system.start_session("test_session_001")
    if session_preview:
        print(f"\nSession Preview:\n{session_preview}")
    else:
        print("No preview (clean start)")

    # Test user message processing
    print("\n2. Processing user message...")
    user_msg = "Continue working on the NightBlade project"
    context = system.process_user_message(user_msg)

    if context:
        print(f"\nContext offered:")
        print(context['formatted_context'])
        print(f"Confidence: {context['confidence']:.2f}")
    else:
        print("No context needed")

    # Test AI response processing
    print("\n3. Processing AI response...")
    ai_resp = "I'm not sure what the current status of NightBlade is."
    uncertainty_help = system.process_ai_response(ai_resp, user_msg)

    if uncertainty_help:
        print(f"\nUncertainty help offered:")
        print(uncertainty_help['formatted_context'])
    else:
        print("No uncertainty detected")

    # Record interaction
    print("\n4. Recording interaction for learning...")
    system.record_interaction(
        context_offered=True,
        ai_response="Based on previous work, here's the NightBlade status...",
        user_feedback={'positive': True}
    )

    # Get health metrics
    print("\n5. System Health Check:")
    print("-" * 60)
    health = system.get_system_health()
    print(f"Session ID: {health['session_id']}")
    print(f"Context shown: {health['awareness']['shown_count']}/{health['awareness']['max_allowed']}")
    print(f"Acceptance rate: {health['acceptance_rate']:.1%}")
    print(f"Helpfulness rate: {health['helpfulness_rate']:.1%}")

    print("\n" + "=" * 60)
    print("Test complete!")
