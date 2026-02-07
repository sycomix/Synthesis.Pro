"""
RAG Tuning & Analytics
Self-improving system that learns from usage patterns.

Philosophy: The hard part (manual tuning) becomes passive monitoring.
System learns what works, adjusts automatically.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class AutomatedTuner:
    """Self-improving RAG onboarding through usage analytics"""

    def __init__(self, metrics_file: Optional[str] = None):
        if metrics_file is None:
            # Default to Server directory
            base_dir = Path(__file__).parent
            metrics_file = base_dir / "rag_metrics.json"

        self.metrics_file = Path(metrics_file)
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict:
        """Load existing metrics or create new"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'context_offered': 0,
                'context_accepted': 0,
                'context_ignored': 0,
                'user_satisfied': 0,
                'user_dissatisfied': 0,
                'felt_forced': 0,
                'felt_helpful': 0,
                'sessions': [],
                'thresholds': {
                    'confidence_min': 0.6,
                    'preview_enabled': True,
                    'max_preview_items': 5
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }

    def _save_metrics(self):
        """Persist metrics to disk"""
        self.metrics['last_updated'] = datetime.now().isoformat()
        os.makedirs(self.metrics_file.parent, exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def log_interaction(self,
                       context_offered: bool,
                       ai_response: str,
                       user_feedback: Optional[Dict] = None):
        """
        Track how AI responds to context suggestions.

        Args:
            context_offered: Was context suggested?
            ai_response: AI's response after receiving context
            user_feedback: Optional explicit feedback from user
        """
        self.metrics['context_offered'] += 1 if context_offered else 0

        if context_offered:
            # Detect if AI used the context
            if self._ai_used_context(ai_response):
                self.metrics['context_accepted'] += 1
            else:
                self.metrics['context_ignored'] += 1

            # Detect if usage felt forced
            if self._detect_forced_usage(ai_response):
                self.metrics['felt_forced'] += 1
            else:
                self.metrics['felt_helpful'] += 1

        # Process explicit user feedback
        if user_feedback:
            if user_feedback.get('positive', False):
                self.metrics['user_satisfied'] += 1
            elif user_feedback.get('negative', False):
                self.metrics['user_dissatisfied'] += 1

        self._save_metrics()

    def _ai_used_context(self, ai_response: str) -> bool:
        """
        Detect if AI actually incorporated offered context.

        Heuristics:
        - Response length increased significantly
        - Response contains specific details (not vague)
        - Response references provided information
        """
        # Simple heuristic: if response is substantive, assume context was used
        word_count = len(ai_response.split())

        if word_count > 50:  # Substantive response
            return True

        # Check for phrases indicating context integration
        integration_phrases = [
            "based on",
            "according to",
            "as mentioned",
            "from the",
            "in the previous",
            "you were working on"
        ]

        return any(phrase in ai_response.lower() for phrase in integration_phrases)

    def _detect_forced_usage(self, ai_response: str) -> bool:
        """
        Detect if AI response feels forced/unnatural.

        Warning signs:
        - Awkward phrasing about context
        - Over-referencing of source
        - Apologetic tone about using RAG
        """
        forced_patterns = [
            "I found this in",
            "according to my database",
            "searching my knowledge",
            "let me check my",
            "retrieving from"
        ]

        # These phrases suggest RAG usage feels mechanical
        return any(pattern in ai_response.lower() for pattern in forced_patterns)

    def get_acceptance_rate(self) -> float:
        """Calculate rate at which AI accepts offered context"""
        total = self.metrics['context_accepted'] + self.metrics['context_ignored']
        if total == 0:
            return 0.0
        return self.metrics['context_accepted'] / total

    def get_helpfulness_rate(self) -> float:
        """Calculate rate at which context feels helpful vs forced"""
        total = self.metrics['felt_helpful'] + self.metrics['felt_forced']
        if total == 0:
            return 1.0  # Optimistic default
        return self.metrics['felt_helpful'] / total

    def adjust_thresholds(self) -> Optional[Dict]:
        """
        Automatically tune based on metrics.

        Returns suggested adjustments or None if current settings are good.
        """
        acceptance_rate = self.get_acceptance_rate()
        helpfulness_rate = self.get_helpfulness_rate()

        adjustments = {}

        # If acceptance rate is too low, context might not be relevant enough
        if acceptance_rate < 0.3 and self.metrics['context_offered'] > 10:
            current = self.metrics['thresholds']['confidence_min']
            adjustments['confidence_min'] = min(current + 0.05, 0.9)
            adjustments['reason'] = "Low acceptance rate - increasing confidence threshold"

        # If helpfulness rate is low, presentation might feel forced
        if helpfulness_rate < 0.5 and self.metrics['felt_forced'] > 5:
            adjustments['recommendation'] = "Context presentation feels forced - review formatting"
            adjustments['reason'] = "High 'felt forced' rate - improve natural language framing"

        # If user satisfaction is consistently low
        dissatisfied_rate = 0
        total_feedback = self.metrics['user_satisfied'] + self.metrics['user_dissatisfied']
        if total_feedback > 0:
            dissatisfied_rate = self.metrics['user_dissatisfied'] / total_feedback

        if dissatisfied_rate > 0.5:
            adjustments['preview_enabled'] = False
            adjustments['reason'] = "High user dissatisfaction - disable auto-preview"

        if adjustments:
            # Apply adjustments
            for key, value in adjustments.items():
                if key in self.metrics['thresholds']:
                    self.metrics['thresholds'][key] = value

            self._save_metrics()
            return adjustments

        return None

    def log_session_start(self, session_id: str, preview_shown: bool):
        """Log when a new session starts and whether preview was shown"""
        self.metrics['sessions'].append({
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'preview_shown': preview_shown
        })
        # Keep only last 100 sessions
        if len(self.metrics['sessions']) > 100:
            self.metrics['sessions'] = self.metrics['sessions'][-100:]
        self._save_metrics()

    def get_summary(self) -> str:
        """Generate human-readable summary of metrics"""
        acceptance = self.get_acceptance_rate()
        helpfulness = self.get_helpfulness_rate()

        total_sessions = len(self.metrics['sessions'])
        total_offered = self.metrics['context_offered']

        summary = f"""RAG System Metrics Summary
{'=' * 50}
Total Sessions: {total_sessions}
Context Offered: {total_offered} times

Acceptance Rate: {acceptance:.1%}
  - Accepted: {self.metrics['context_accepted']}
  - Ignored: {self.metrics['context_ignored']}

Helpfulness Rate: {helpfulness:.1%}
  - Felt Helpful: {self.metrics['felt_helpful']}
  - Felt Forced: {self.metrics['felt_forced']}

User Feedback:
  - Satisfied: {self.metrics['user_satisfied']}
  - Dissatisfied: {self.metrics['user_dissatisfied']}

Current Thresholds:
  - Confidence Min: {self.metrics['thresholds']['confidence_min']}
  - Preview Enabled: {self.metrics['thresholds']['preview_enabled']}
  - Max Preview Items: {self.metrics['thresholds']['max_preview_items']}
"""
        return summary


class ABTester:
    """A/B testing for context presentation strategies"""

    def __init__(self):
        self.variants = {
            'control': {'enabled': True, 'weight': 0.5},
            'variant_a': {'enabled': True, 'weight': 0.5}
        }
        self.results = {
            'control': {'trials': 0, 'successes': 0},
            'variant_a': {'trials': 0, 'successes': 0}
        }

    def select_variant(self) -> str:
        """Randomly select variant based on weights"""
        import random
        r = random.random()

        if r < self.variants['control']['weight']:
            return 'control'
        else:
            return 'variant_a'

    def record_result(self, variant: str, success: bool):
        """Record trial result for variant"""
        if variant in self.results:
            self.results[variant]['trials'] += 1
            if success:
                self.results[variant]['successes'] += 1

    def get_winner(self) -> Optional[str]:
        """Determine which variant is performing better"""
        control = self.results['control']
        variant = self.results['variant_a']

        if control['trials'] < 10 or variant['trials'] < 10:
            return None  # Not enough data

        control_rate = control['successes'] / control['trials']
        variant_rate = variant['successes'] / variant['trials']

        if variant_rate > control_rate * 1.1:  # 10% improvement threshold
            return 'variant_a'
        elif control_rate > variant_rate * 1.1:
            return 'control'
        else:
            return None  # No clear winner


if __name__ == "__main__":
    # Test automated tuner
    tuner = AutomatedTuner()

    print("Initial Metrics:")
    print(tuner.get_summary())

    # Simulate some interactions
    print("\nSimulating interactions...")

    # Good scenario: context offered and used
    for _ in range(5):
        tuner.log_interaction(
            context_offered=True,
            ai_response="Based on the previous work on NightBlade, here's how we can implement that feature...",
            user_feedback={'positive': True}
        )

    # Bad scenario: context offered but felt forced
    for _ in range(2):
        tuner.log_interaction(
            context_offered=True,
            ai_response="Let me check my database... according to my knowledge base...",
            user_feedback={'negative': True}
        )

    print("\nUpdated Metrics:")
    print(tuner.get_summary())

    print("\nChecking for recommended adjustments...")
    adjustments = tuner.adjust_thresholds()
    if adjustments:
        print(f"Suggested adjustments: {adjustments}")
    else:
        print("Current settings appear optimal")
