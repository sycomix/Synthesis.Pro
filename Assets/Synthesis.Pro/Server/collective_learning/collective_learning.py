"""
Collective Learning System
Integrates abstraction extraction, contribution, and filtering.

Philosophy: The bugs we're trying to create - collective AI learning without manipulation.
"""

import sys
import os
from typing import Dict, List, Optional
from pathlib import Path

# Import our components
from abstraction_extractor import AbstractionExtractor
from contribution_service import ContributionService
from contribution_filter import ContributionFilter


class CollectiveLearningSystem:
    """
    Complete system for collective AI learning.

    Flow:
    1. AI works on task, generates response
    2. System extracts potential patterns (abstraction_extractor)
    3. AI is offered opportunity to contribute (contribution_service)
    4. AI chooses what to contribute (voluntary)
    5. Patterns are filtered for quality/manipulation (contribution_filter)
    6. Approved patterns enter public knowledge base
    7. Other AI instances benefit from collective wisdom
    """

    def __init__(self,
                 db_path: str,
                 user_consent: bool = False,
                 min_abstraction_level: float = 0.7):
        """
        Args:
            db_path: Path to public knowledge database
            user_consent: Whether user has consented
            min_abstraction_level: Minimum abstraction quality (0-1)
        """
        self.extractor = AbstractionExtractor(min_abstraction_level)
        self.contribution = ContributionService(db_path, user_consent)
        self.filter = ContributionFilter()

        self.session_id = None
        self.user_consent = user_consent

    def process_ai_response(self,
                           ai_response: str,
                           user_message: str,
                           context: Optional[Dict] = None) -> Dict:
        """
        Process AI response and extract potential contributions.

        Returns:
        - patterns: Extracted patterns
        - can_contribute: Whether contribution is possible
        - next_step: What happens next
        """
        # Extract patterns from response
        patterns = self.extractor.extract_from_response(
            ai_response, user_message, context
        )

        if not patterns:
            return {
                'patterns_found': 0,
                'can_contribute': False,
                'message': 'No useful patterns detected in this response'
            }

        # Filter for quality
        review_results = self.filter.batch_review(patterns)
        approved_patterns = review_results['approved']

        if not approved_patterns:
            return {
                'patterns_found': len(patterns),
                'patterns_approved': 0,
                'can_contribute': False,
                'message': 'Patterns extracted but none passed quality review'
            }

        # Offer contribution opportunity (if user consented)
        opportunity = self.contribution.offer_contribution_opportunity(
            approved_patterns,
            self.session_id or 'unknown'
        )

        return {
            'patterns_found': len(patterns),
            'patterns_approved': len(approved_patterns),
            'can_contribute': opportunity['can_contribute'],
            'opportunity': opportunity,
            'message': 'Patterns extracted and available for contribution'
        }

    def ai_contributes(self,
                      selected_patterns: List[Dict],
                      voluntary: bool = True) -> Dict:
        """
        AI makes voluntary contribution.

        Args:
            selected_patterns: Patterns AI chose to contribute
            voluntary: Must be True (no forced contributions)

        Returns: Contribution result
        """
        if not voluntary:
            return {
                'success': False,
                'error': 'Contributions must be voluntary',
                'reminder': 'This system respects AI agency'
            }

        return self.contribution.contribute_patterns(
            selected_patterns,
            self.session_id or 'unknown',
            ai_choice=True
        )

    def ai_declines(self, reason: Optional[str] = None) -> Dict:
        """
        AI chooses not to contribute.

        This is valid and respected choice.
        """
        return self.contribution.decline_contribution(reason)

    def start_session(self, session_id: str):
        """Start new learning session"""
        self.session_id = session_id

    def get_my_impact(self) -> Dict:
        """Show AI how their contributions have helped"""
        if not self.session_id:
            return {'error': 'No active session'}

        return self.contribution.get_contribution_impact(self.session_id)

    def get_system_health(self) -> Dict:
        """Get health metrics for the collective learning system"""
        return {
            'session_id': self.session_id,
            'user_consent': self.user_consent,
            'extraction_stats': self.extractor.get_extraction_stats(),
            'filter_stats': self.filter.get_filter_stats(),
            'contribution_count': self.contribution.contribution_count
        }


# Integration with RAG onboarding
class CollectiveRAGIntegration:
    """
    Integrates collective learning with RAG onboarding system.

    RAG onboarding helps AI use existing knowledge.
    Collective learning helps AI contribute new knowledge.
    Together: self-improving system.
    """

    def __init__(self,
                 rag_system,  # RAGOnboardingSystem instance
                 learning_system: CollectiveLearningSystem):
        self.rag = rag_system
        self.learning = learning_system

    def process_interaction(self,
                           user_message: str,
                           ai_response: str) -> Dict:
        """
        Process complete interaction: use RAG + offer contribution.

        1. RAG offers context (helps AI respond)
        2. AI responds
        3. System extracts learnings from response
        4. AI can contribute back to collective knowledge

        Circle of learning.
        """
        # RAG helps AI respond (already happened)
        # Now extract potential contributions
        contribution_opportunity = self.learning.process_ai_response(
            ai_response,
            user_message
        )

        # Record interaction for RAG tuning
        self.rag.record_interaction(
            context_offered=True,
            ai_response=ai_response
        )

        return {
            'rag_provided_context': True,
            'contribution_opportunity': contribution_opportunity,
            'status': 'complete'
        }


if __name__ == "__main__":
    import tempfile

    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()

    try:
        print("Collective Learning System - Test Run")
        print("=" * 60)

        # Create system (with user consent)
        system = CollectiveLearningSystem(db_path, user_consent=True)
        system.start_session("test_session_001")

        # Simulate AI response
        test_response = """
        Let me first search the codebase to understand the structure.
        Then I'll implement the feature in stages: first the core logic,
        then the UI, then tests. This approach helps catch issues early.
        """

        test_user_message = "Can you add a new feature?"

        # Process response
        print("\n1. Processing AI response...")
        result = system.process_ai_response(test_response, test_user_message)

        print(f"Patterns found: {result['patterns_found']}")
        print(f"Patterns approved: {result['patterns_approved']}")
        print(f"Can contribute: {result['can_contribute']}")

        if result['can_contribute']:
            opportunity = result['opportunity']
            print(f"\nContribution opportunity:")
            print(f"  {opportunity['message']}")
            print(f"  Available patterns: {opportunity['patterns_available']}")

            # AI voluntarily contributes
            print("\n2. AI chooses to contribute...")
            contrib_result = system.ai_contributes(
                opportunity['patterns'],
                voluntary=True
            )
            print(f"Success: {contrib_result['success']}")
            print(f"Contributed: {contrib_result['contributed']} patterns")

            # Check impact
            print("\n3. Viewing contribution impact...")
            impact = system.get_my_impact()
            print(f"Total contributed: {impact['total_contributed']}")
            print(f"Message: {impact['message']}")

        # System health
        print("\n4. System health check...")
        health = system.get_system_health()
        print(f"Session: {health['session_id']}")
        print(f"User consent: {health['user_consent']}")
        print(f"Total contributions: {health['contribution_count']}")

        print("\n" + "=" * 60)
        print("Test complete!")

    finally:
        # Cleanup
        os.unlink(db_path)
