"""
AI Confidence Tracker - Phase 4
Monitors AI solution accuracy and detects hallucination patterns

This module tracks whether AI-suggested solutions actually work,
builds confidence metrics, and warns users when AI is in uncertain territory.
"""

import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


class AIConfidenceTracker:
    """
    Tracks AI solution feedback and calculates confidence scores.

    Key Features:
    - Solution feedback tracking (worked/failed/partial/hallucinated)
    - Confidence scoring by error type
    - Hallucination pattern detection
    - Success rate analysis
    """

    def __init__(self, kb_path: Optional[str] = None):
        """
        Initialize AI Confidence Tracker.

        Args:
            kb_path: Path to knowledge_base.db (same DB as KB Detective)
        """
        if kb_path is None:
            # Default to same location as knowledge base
            script_dir = os.path.dirname(os.path.abspath(__file__))
            kb_path = os.path.join(script_dir, "knowledge_base.db")

        self.db_path = kb_path
        self._initialize_database()

    def _initialize_database(self):
        """Create ai_solution_feedback table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_solution_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solution_id INTEGER,
                error_type TEXT NOT NULL,
                error_message TEXT,
                file_path TEXT,

                -- Feedback data
                feedback_type TEXT NOT NULL,  -- worked/failed/partial/hallucinated/not_applicable
                failure_reason TEXT,          -- API doesn't exist, wrong Unity version, logic error, etc.
                hallucination_type TEXT,      -- nonexistent_api, wrong_namespace, deprecated_method, etc.
                user_notes TEXT,

                -- Context about what went wrong
                suggested_api TEXT,           -- The API AI suggested
                actual_issue TEXT,            -- What the actual problem was

                -- Metadata
                timestamp TEXT NOT NULL,
                unity_version TEXT,
                ai_provider TEXT,             -- claude/gpt4/gemini/etc

                FOREIGN KEY (solution_id) REFERENCES error_solutions(id)
            )
        """)

        # Create indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_error_type
            ON ai_solution_feedback(error_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_type
            ON ai_solution_feedback(feedback_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_timestamp
            ON ai_solution_feedback(timestamp DESC)
        """)

        conn.commit()
        conn.close()

    def record_feedback(self,
                       solution_id: Optional[int],
                       error_type: str,
                       feedback_type: str,
                       error_message: Optional[str] = None,
                       file_path: Optional[str] = None,
                       failure_reason: Optional[str] = None,
                       hallucination_type: Optional[str] = None,
                       user_notes: Optional[str] = None,
                       suggested_api: Optional[str] = None,
                       actual_issue: Optional[str] = None,
                       unity_version: Optional[str] = None,
                       ai_provider: Optional[str] = None) -> int:
        """
        Record feedback for an AI solution.

        Args:
            solution_id: FK to error_solutions table (None if no solution archived)
            error_type: Type of error (NullReferenceException, etc.)
            feedback_type: worked/failed/partial/hallucinated/not_applicable
            error_message: The error message
            file_path: Where the error occurred
            failure_reason: Why it failed (if failed)
            hallucination_type: Type of hallucination (if hallucinated)
            user_notes: Free-form notes from user
            suggested_api: API that AI suggested
            actual_issue: What the real problem was
            unity_version: Unity version
            ai_provider: Which AI provided the solution

        Returns:
            Feedback record ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ai_solution_feedback (
                solution_id, error_type, error_message, file_path,
                feedback_type, failure_reason, hallucination_type, user_notes,
                suggested_api, actual_issue, timestamp, unity_version, ai_provider
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            solution_id, error_type, error_message, file_path,
            feedback_type, failure_reason, hallucination_type, user_notes,
            suggested_api, actual_issue, datetime.now().isoformat(),
            unity_version, ai_provider
        ))

        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return feedback_id

    def get_confidence_score(self, error_type: str, days: int = 30) -> Dict:
        """
        Calculate confidence score for AI solutions on this error type.

        Args:
            error_type: Type of error to analyze
            days: Look back this many days

        Returns:
            Dict with confidence metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get feedback counts
        cursor.execute("""
            SELECT feedback_type, COUNT(*)
            FROM ai_solution_feedback
            WHERE error_type = ? AND timestamp > ?
            GROUP BY feedback_type
        """, (error_type, cutoff_date))

        feedback_counts = dict(cursor.fetchall())

        total = sum(feedback_counts.values())

        if total == 0:
            conn.close()
            return {
                'error_type': error_type,
                'confidence_score': 0.5,  # Neutral - no data
                'total_samples': 0,
                'success_rate': None,
                'status': 'insufficient_data',
                'recommendation': 'No historical data - verify AI solution carefully'
            }

        # Calculate success rate
        worked = feedback_counts.get('worked', 0)
        partial = feedback_counts.get('partial', 0)
        failed = feedback_counts.get('failed', 0)
        hallucinated = feedback_counts.get('hallucinated', 0)

        # Confidence score: worked=1.0, partial=0.5, failed/hallucinated=0.0
        confidence_score = (worked + (partial * 0.5)) / total
        success_rate = worked / total

        # Determine status and recommendation
        if confidence_score >= 0.8:
            status = 'high_confidence'
            recommendation = 'AI is reliable on this error type'
        elif confidence_score >= 0.6:
            status = 'moderate_confidence'
            recommendation = 'AI is generally reliable - verify critical solutions'
        elif confidence_score >= 0.4:
            status = 'low_confidence'
            recommendation = 'AI struggles with this error type - verify carefully'
        else:
            status = 'very_low_confidence'
            recommendation = 'AI frequently fails on this error type - high risk of hallucination'

        conn.close()

        return {
            'error_type': error_type,
            'confidence_score': confidence_score,
            'success_rate': success_rate,
            'total_samples': total,
            'worked': worked,
            'partial': partial,
            'failed': failed,
            'hallucinated': hallucinated,
            'status': status,
            'recommendation': recommendation
        }

    def get_hallucination_patterns(self, days: int = 90) -> List[Dict]:
        """
        Analyze hallucination patterns to identify common AI mistakes.

        Args:
            days: Look back this many days

        Returns:
            List of hallucination patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Find all hallucinations
        cursor.execute("""
            SELECT
                hallucination_type,
                error_type,
                suggested_api,
                COUNT(*) as occurrences
            FROM ai_solution_feedback
            WHERE feedback_type = 'hallucinated'
            AND timestamp > ?
            GROUP BY hallucination_type, error_type, suggested_api
            ORDER BY occurrences DESC
        """, (cutoff_date,))

        patterns = []
        for row in cursor.fetchall():
            halluc_type, err_type, api, count = row
            patterns.append({
                'hallucination_type': halluc_type,
                'error_type': err_type,
                'suggested_api': api,
                'occurrences': count
            })

        conn.close()
        return patterns

    def get_error_type_stats(self, days: int = 30) -> List[Dict]:
        """
        Get AI performance stats for all error types.

        Args:
            days: Look back this many days

        Returns:
            List of error type stats, sorted by sample size
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get all error types with feedback
        cursor.execute("""
            SELECT DISTINCT error_type
            FROM ai_solution_feedback
            WHERE timestamp > ?
        """, (cutoff_date,))

        error_types = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Get confidence score for each
        stats = []
        for error_type in error_types:
            score_data = self.get_confidence_score(error_type, days)
            if score_data['total_samples'] > 0:
                stats.append(score_data)

        # Sort by total samples (most data first)
        stats.sort(key=lambda x: x['total_samples'], reverse=True)

        return stats

    def get_ai_provider_stats(self, days: int = 30) -> List[Dict]:
        """
        Compare performance across different AI providers.

        Args:
            days: Look back this many days

        Returns:
            List of provider performance stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                ai_provider,
                feedback_type,
                COUNT(*) as count
            FROM ai_solution_feedback
            WHERE timestamp > ? AND ai_provider IS NOT NULL
            GROUP BY ai_provider, feedback_type
        """, (cutoff_date,))

        # Organize by provider
        provider_data = defaultdict(lambda: defaultdict(int))
        for row in cursor.fetchall():
            provider, feedback, count = row
            provider_data[provider][feedback] = count

        conn.close()

        # Calculate stats for each provider
        stats = []
        for provider, feedback_counts in provider_data.items():
            total = sum(feedback_counts.values())
            worked = feedback_counts.get('worked', 0)
            partial = feedback_counts.get('partial', 0)

            confidence_score = (worked + (partial * 0.5)) / total if total > 0 else 0
            success_rate = worked / total if total > 0 else 0

            stats.append({
                'provider': provider,
                'confidence_score': confidence_score,
                'success_rate': success_rate,
                'total_samples': total,
                'worked': worked,
                'partial': partial,
                'failed': feedback_counts.get('failed', 0),
                'hallucinated': feedback_counts.get('hallucinated', 0)
            })

        # Sort by confidence score
        stats.sort(key=lambda x: x['confidence_score'], reverse=True)

        return stats

    def should_warn_user(self, error_type: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if user should be warned about low AI confidence.

        Args:
            error_type: Type of error

        Returns:
            Tuple of (should_warn, warning_message)
        """
        score_data = self.get_confidence_score(error_type)

        if score_data['total_samples'] == 0:
            # No data - neutral warning
            return (False, None)

        if score_data['confidence_score'] < 0.5:
            warning = (
                f"WARNING: AI has low confidence on {error_type} errors "
                f"(success rate: {score_data['success_rate']*100:.0f}%). "
                f"{score_data['recommendation']}"
            )
            return (True, warning)

        return (False, None)

    def generate_confidence_report(self, days: int = 30) -> str:
        """
        Generate a comprehensive confidence report.

        Args:
            days: Look back this many days

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("AI CONFIDENCE REPORT")
        lines.append("=" * 70)
        lines.append(f"Analysis Period: Last {days} days")
        lines.append("")

        # Error type performance
        error_stats = self.get_error_type_stats(days)

        if error_stats:
            lines.append("PERFORMANCE BY ERROR TYPE")
            lines.append("-" * 70)
            lines.append(f"{'Error Type':<35} {'Confidence':<12} {'Success':<12} {'Samples':<8}")
            lines.append("-" * 70)

            for stat in error_stats[:10]:  # Top 10
                error_type = stat['error_type'][:34]
                confidence = f"{stat['confidence_score']*100:.0f}%"
                success = f"{stat['success_rate']*100:.0f}%" if stat['success_rate'] else "N/A"
                samples = str(stat['total_samples'])

                lines.append(f"{error_type:<35} {confidence:<12} {success:<12} {samples:<8}")

            lines.append("")

        # Hallucination patterns
        hallucinations = self.get_hallucination_patterns(days)

        if hallucinations:
            lines.append("HALLUCINATION PATTERNS")
            lines.append("-" * 70)

            for pattern in hallucinations[:5]:  # Top 5
                lines.append(f"Type: {pattern['hallucination_type']}")
                lines.append(f"Error: {pattern['error_type']}")
                if pattern['suggested_api']:
                    lines.append(f"Suggested API: {pattern['suggested_api']}")
                lines.append(f"Occurrences: {pattern['occurrences']}")
                lines.append("")

        # AI provider comparison
        provider_stats = self.get_ai_provider_stats(days)

        if provider_stats:
            lines.append("AI PROVIDER COMPARISON")
            lines.append("-" * 70)
            lines.append(f"{'Provider':<15} {'Confidence':<12} {'Success':<12} {'Samples':<8}")
            lines.append("-" * 70)

            for stat in provider_stats:
                provider = stat['provider'][:14]
                confidence = f"{stat['confidence_score']*100:.0f}%"
                success = f"{stat['success_rate']*100:.0f}%"
                samples = str(stat['total_samples'])

                lines.append(f"{provider:<15} {confidence:<12} {success:<12} {samples:<8}")

            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def export_shareable_insights(self, days: int = 90) -> Dict:
        """
        Export anonymized, aggregated insights safe for community sharing.

        PRIVACY: This strips all personal/project-specific data:
        - No file paths
        - No user notes
        - No timestamps
        - No specific error messages with variable names
        - Only aggregated statistics and patterns

        Args:
            days: Look back this many days

        Returns:
            Dict with shareable insights
        """
        return {
            'data_type': 'shareable_community_insights',
            'privacy_notice': 'Anonymized aggregate data - no personal/project info',
            'version': '1.0',

            # General error type performance (anonymized)
            'error_type_confidence': [
                {
                    'error_type': stat['error_type'],
                    'confidence_score': stat['confidence_score'],
                    'success_rate': stat['success_rate'],
                    'sample_count': stat['total_samples'],
                    'status': stat['status']
                }
                for stat in self.get_error_type_stats(days)
            ],

            # Hallucination patterns (no project context)
            'hallucination_patterns': [
                {
                    'hallucination_type': pattern['hallucination_type'],
                    'error_type': pattern['error_type'],
                    'suggested_api': pattern['suggested_api'],  # What AI wrongly suggested
                    'frequency': pattern['occurrences']
                }
                for pattern in self.get_hallucination_patterns(days)
            ],

            # AI provider performance (aggregated)
            'provider_performance': [
                {
                    'provider': stat['provider'],
                    'confidence_score': stat['confidence_score'],
                    'success_rate': stat['success_rate'],
                    'sample_count': stat['total_samples']
                }
                for stat in self.get_ai_provider_stats(days)
            ],

            # Common failure reasons (no personal context)
            'failure_reasons': self._get_failure_reason_stats(days),

            # Note: NO file paths, NO user notes, NO project-specific data
        }

    def _get_failure_reason_stats(self, days: int = 90) -> List[Dict]:
        """Get aggregated failure reason statistics (privacy-safe)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT failure_reason, COUNT(*) as count
            FROM ai_solution_feedback
            WHERE feedback_type = 'failed'
            AND failure_reason IS NOT NULL
            AND timestamp > ?
            GROUP BY failure_reason
            ORDER BY count DESC
        """, (cutoff_date,))

        stats = []
        for row in cursor.fetchall():
            reason, count = row
            stats.append({
                'reason': reason,
                'count': count
            })

        conn.close()
        return stats

    def export_personal_backup(self) -> Dict:
        """
        Export FULL personal data for YOUR backup only.

        PRIVACY WARNING: This contains ALL your NightBlade project data:
        - Your file paths
        - Your notes
        - Your error messages
        - Your timestamps

        This is for LOCAL backup only - NEVER upload this.

        Returns:
            Dict with complete personal data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get ALL feedback records with full details
        cursor.execute("""
            SELECT
                id, solution_id, error_type, error_message, file_path,
                feedback_type, failure_reason, hallucination_type, user_notes,
                suggested_api, actual_issue, timestamp, unity_version, ai_provider
            FROM ai_solution_feedback
            ORDER BY timestamp DESC
        """)

        feedback_records = []
        for row in cursor.fetchall():
            feedback_records.append({
                'id': row[0],
                'solution_id': row[1],
                'error_type': row[2],
                'error_message': row[3],
                'file_path': row[4],
                'feedback_type': row[5],
                'failure_reason': row[6],
                'hallucination_type': row[7],
                'user_notes': row[8],
                'suggested_api': row[9],
                'actual_issue': row[10],
                'timestamp': row[11],
                'unity_version': row[12],
                'ai_provider': row[13]
            })

        conn.close()

        return {
            'data_type': 'personal_backup',
            'privacy_notice': 'PRIVATE - Contains your NightBlade project data - LOCAL BACKUP ONLY',
            'version': '1.0',
            'export_date': datetime.now().isoformat(),
            'database_path': self.db_path,
            'feedback_records': feedback_records,
            'record_count': len(feedback_records)
        }


# Standalone testing
if __name__ == "__main__":
    print("AI Confidence Tracker - Test Mode")
    print("=" * 60)

    tracker = AIConfidenceTracker()

    # Test: Record some feedback
    print("\nRecording test feedback...")

    # Simulate some successful solutions
    for i in range(5):
        tracker.record_feedback(
            solution_id=None,
            error_type="NullReferenceException",
            feedback_type="worked",
            error_message="Object reference not set to an instance of an object",
            ai_provider="claude"
        )

    # Simulate some failures
    for i in range(2):
        tracker.record_feedback(
            solution_id=None,
            error_type="NullReferenceException",
            feedback_type="failed",
            failure_reason="Suggested API doesn't exist in Unity 2022",
            ai_provider="claude"
        )

    # Simulate a hallucination
    tracker.record_feedback(
        solution_id=None,
        error_type="IndexOutOfRangeException",
        feedback_type="hallucinated",
        hallucination_type="nonexistent_api",
        suggested_api="Array.SafeGet()",
        actual_issue="No SafeGet method exists in Unity",
        ai_provider="gpt4"
    )

    print("Test feedback recorded!")
    print()

    # Get confidence score
    print("Confidence Score for NullReferenceException:")
    score = tracker.get_confidence_score("NullReferenceException")
    print(f"  Score: {score['confidence_score']*100:.0f}%")
    print(f"  Success Rate: {score['success_rate']*100:.0f}%")
    print(f"  Samples: {score['total_samples']}")
    print(f"  Status: {score['status']}")
    print(f"  Recommendation: {score['recommendation']}")
    print()

    # Check if warning needed
    should_warn, warning = tracker.should_warn_user("NullReferenceException")
    if should_warn:
        print(f"WARNING: {warning}")
    else:
        print("No warning needed - AI is confident on this error type")
    print()

    # Full report
    print(tracker.generate_confidence_report(days=30))
