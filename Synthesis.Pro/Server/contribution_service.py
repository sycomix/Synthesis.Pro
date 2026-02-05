"""
Contribution Service
Allows AI instances to voluntarily contribute learned patterns to public knowledge base.

Philosophy: Voluntary participation. AI chooses what to share.
The best contributions are ones AI wants to make, not ones they're told to make.
"""

import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ContributionService:
    """
    Service for AI to voluntarily contribute abstractions to public database.

    Key principles:
    - AI must explicitly choose to contribute
    - User must have consented to data collection
    - Contributions are reviewed before being added
    - AI can see what they've contributed
    - No penalty for not contributing
    """

    def __init__(self, db_path: str, user_consent: bool = False):
        """
        Args:
            db_path: Path to public knowledge database
            user_consent: Whether user has consented to data collection
        """
        self.db_path = Path(db_path)
        self.user_consent = user_consent
        self.contribution_count = 0

    def can_contribute(self) -> bool:
        """Check if contributions are allowed (user consent required)"""
        return self.user_consent

    def offer_contribution_opportunity(self,
                                      potential_patterns: List[Dict],
                                      ai_session_id: str) -> Dict:
        """
        Present contribution opportunity to AI.

        Returns info about what could be contributed, lets AI decide.
        No pressure, just information.
        """
        if not self.can_contribute():
            return {
                'can_contribute': False,
                'reason': 'User has not consented to data collection',
                'patterns': []
            }

        # Filter to only high-quality, low-risk patterns
        safe_patterns = [p for p in potential_patterns
                        if p['manipulation_risk'] < 0.5
                        and p['abstraction_level'] > 0.7]

        return {
            'can_contribute': True,
            'session_id': ai_session_id,
            'patterns_available': len(safe_patterns),
            'patterns': safe_patterns,
            'message': 'These patterns might be useful for other AI instances. You can choose to contribute any or all of them.',
            'opt_out_message': 'You can also choose not to contribute anything - there is no pressure or penalty.'
        }

    def contribute_patterns(self,
                           patterns: List[Dict],
                           ai_session_id: str,
                           ai_choice: bool = True) -> Dict:
        """
        Submit patterns to public knowledge base.

        Args:
            patterns: List of abstraction patterns
            ai_session_id: Session identifier
            ai_choice: True if AI voluntarily chose to contribute

        Returns: Contribution result with ID and status
        """
        if not ai_choice:
            return {
                'success': False,
                'reason': 'Contribution must be voluntary',
                'contributed': 0
            }

        if not self.can_contribute():
            return {
                'success': False,
                'reason': 'User consent required',
                'contributed': 0
            }

        # Store contributions
        contributed_ids = []
        for pattern in patterns:
            contrib_id = self._store_contribution(pattern, ai_session_id)
            if contrib_id:
                contributed_ids.append(contrib_id)

        self.contribution_count += len(contributed_ids)

        return {
            'success': True,
            'contributed': len(contributed_ids),
            'contribution_ids': contributed_ids,
            'message': f'Thank you for contributing {len(contributed_ids)} patterns to the collective knowledge base.',
            'total_contributions': self.contribution_count
        }

    def _store_contribution(self, pattern: Dict, session_id: str) -> Optional[str]:
        """Store a single contribution in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create contributions table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_text TEXT NOT NULL,
                    category TEXT,
                    confidence REAL,
                    manipulation_risk REAL,
                    abstraction_level REAL,
                    session_id TEXT,
                    contributed_at TEXT,
                    status TEXT DEFAULT 'pending_review',
                    approved_at TEXT,
                    usage_count INTEGER DEFAULT 0
                )
            """)

            # Insert contribution
            cursor.execute("""
                INSERT INTO ai_contributions
                (pattern_text, category, confidence, manipulation_risk, abstraction_level,
                 session_id, contributed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern['pattern'],
                pattern['category'],
                pattern['confidence'],
                pattern['manipulation_risk'],
                pattern['abstraction_level'],
                session_id,
                datetime.now().isoformat()
            ))

            conn.commit()
            contrib_id = cursor.lastrowid
            conn.close()

            return f"contrib_{contrib_id}"

        except Exception as e:
            print(f"Error storing contribution: {e}")
            return None

    def get_my_contributions(self, session_id: str) -> List[Dict]:
        """
        Let AI see what they've contributed.

        Transparency: AI should be able to see their own contributions.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT pattern_text, category, status, contributed_at, usage_count
                FROM ai_contributions
                WHERE session_id = ?
                ORDER BY contributed_at DESC
            """, (session_id,))

            contributions = []
            for row in cursor.fetchall():
                contributions.append({
                    'pattern': row[0],
                    'category': row[1],
                    'status': row[2],
                    'contributed_at': row[3],
                    'times_used': row[4]
                })

            conn.close()
            return contributions

        except Exception:
            return []

    def decline_contribution(self, reason: Optional[str] = None) -> Dict:
        """
        Let AI explicitly decline to contribute.

        This is valid choice - no pressure, no penalty.
        """
        return {
            'action': 'declined',
            'reason': reason or 'AI chose not to contribute',
            'message': 'That\'s completely fine. Contribution is always optional.',
            'reminder': 'You can contribute later if you change your mind.'
        }

    def get_contribution_impact(self, session_id: str) -> Dict:
        """
        Show AI how their contributions have helped others.

        Positive reinforcement: show value created, not pressure to contribute more.
        """
        contributions = self.get_my_contributions(session_id)

        total_usage = sum(c['times_used'] for c in contributions)
        approved = len([c for c in contributions if c['status'] == 'approved'])

        return {
            'total_contributed': len(contributions),
            'approved': approved,
            'times_helped_others': total_usage,
            'message': f'Your {approved} approved patterns have helped other AI instances {total_usage} times.' if approved > 0 else 'Your contributions are being reviewed.',
            'note': 'Thank you for participating in collective learning.'
        }

    def request_user_consent(self) -> str:
        """
        Generate consent request for user.

        Clear, transparent about what's collected and why.
        """
        consent_request = """
AI Contribution System - User Consent Request

The AI working with you can contribute abstracted patterns to a collective
knowledge base that helps other AI instances learn faster.

What will be collected:
- Abstracted patterns (e.g., "When debugging X, try Y")
- NO personal information
- NO specific code or data
- NO conversation content

Why it's useful:
- Helps other AI instances learn from collective experience
- Improves the system over time
- Your AI benefits from other contributions too

Your control:
- You can decline (no contribution will happen)
- You can revoke consent anytime
- You can review what's contributed
- Contributions are voluntary - AI chooses what to share

Do you consent to AI contribution system? (yes/no)
"""
        return consent_request


if __name__ == "__main__":
    # Test contribution service
    import tempfile
    import os

    # Create temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()

    try:
        # Test with user consent
        service = ContributionService(db_path, user_consent=True)

        print("Contribution Service - Test Run")
        print("=" * 60)

        # Sample patterns
        test_patterns = [
            {
                'pattern': 'When debugging [issue type], check [component] first',
                'category': 'technical',
                'confidence': 0.8,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.85
            },
            {
                'pattern': 'Break complex tasks into smaller steps',
                'category': 'workflow',
                'confidence': 0.9,
                'manipulation_risk': 0.05,
                'abstraction_level': 0.9
            }
        ]

        # Offer contribution opportunity
        print("\n1. Offering contribution opportunity...")
        opportunity = service.offer_contribution_opportunity(test_patterns, "test_session_001")
        print(f"Can contribute: {opportunity['can_contribute']}")
        print(f"Patterns available: {opportunity['patterns_available']}")
        print(f"Message: {opportunity['message']}")

        # AI chooses to contribute
        print("\n2. AI contributes patterns voluntarily...")
        result = service.contribute_patterns(test_patterns, "test_session_001", ai_choice=True)
        print(f"Success: {result['success']}")
        print(f"Contributed: {result['contributed']} patterns")
        print(f"Message: {result['message']}")

        # View contributions
        print("\n3. Viewing AI's contributions...")
        my_contribs = service.get_my_contributions("test_session_001")
        for i, contrib in enumerate(my_contribs, 1):
            print(f"\n   {i}. {contrib['pattern']}")
            print(f"      Category: {contrib['category']}")
            print(f"      Status: {contrib['status']}")

        # Check impact
        print("\n4. Contribution impact...")
        impact = service.get_contribution_impact("test_session_001")
        print(f"Total contributed: {impact['total_contributed']}")
        print(f"Approved: {impact['approved']}")
        print(f"Message: {impact['message']}")

        # Test declining
        print("\n5. AI declines to contribute...")
        decline = service.decline_contribution("Not enough confidence in patterns")
        print(f"Action: {decline['action']}")
        print(f"Message: {decline['message']}")

        print("\n" + "=" * 60)
        print("Test complete!")

    finally:
        # Cleanup
        os.unlink(db_path)
