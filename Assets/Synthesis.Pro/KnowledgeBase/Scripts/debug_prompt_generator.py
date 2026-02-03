"""
Debug Report Generator - AI-optimized error investigation prompts
Part of Synthesis AI Detective Mode

Formats structured debugging prompts that include error details,
code context, Knowledge Base findings, and pattern analysis.

Zero external dependencies - uses only Python standard library.
"""

from typing import Dict, List, Optional
from datetime import datetime


class DebugPromptGenerator:
    """
    Generates structured, context-rich debugging prompts for AI analysis.
    Combines error data, code context, and Knowledge Base intelligence.
    """

    def __init__(self):
        """Initialize the prompt generator."""
        self.templates = {
            'investigation': self._investigation_template,
            'pattern_alert': self._pattern_alert_template,
            'quick_fix': self._quick_fix_template
        }

    def generate_debug_prompt(self,
                             error: Dict,
                             code_context: Optional[str] = None,
                             similar_errors: Optional[List[Dict]] = None,
                             pattern: Optional[Dict] = None,
                             recent_changes: Optional[List[Dict]] = None,
                             template: str = 'investigation') -> str:
        """
        Generate a comprehensive debugging prompt for AI.

        Args:
            error: Error dict from UnityLogDetective
            code_context: Code around error (from extract_code_context)
            similar_errors: Similar past errors (from KnowledgeBaseDetective)
            pattern: Error pattern analysis (from detect_error_pattern)
            recent_changes: Recent file modifications (from get_recent_changes)
            template: Which template to use ('investigation', 'pattern_alert', 'quick_fix')

        Returns:
            Formatted debug prompt string
        """
        template_func = self.templates.get(template, self._investigation_template)
        return template_func(error, code_context, similar_errors, pattern, recent_changes)

    def _investigation_template(self,
                                error: Dict,
                                code_context: Optional[str],
                                similar_errors: Optional[List[Dict]],
                                pattern: Optional[Dict],
                                recent_changes: Optional[List[Dict]]) -> str:
        """
        Full investigation prompt with all available context.
        Use when you need comprehensive AI analysis.
        """
        lines = []

        # Header
        lines.append("🔍 DEBUGGING INVESTIGATION")
        lines.append("=" * 70)
        lines.append("")

        # Error Details
        lines.append("ERROR DETECTED:")
        lines.append(f"Type: {error.get('type', 'Unknown')}")
        lines.append(f"Severity: {error.get('severity', 'unknown').upper()}")

        if error.get('file_path') and error['file_path'] != 'Unknown':
            lines.append(f"File: {error['file_path']}:{error.get('line', 0)}")

        if error.get('method'):
            lines.append(f"Method: {error['method']}")

        if error.get('error_code'):
            lines.append(f"Error Code: {error['error_code']}")

        lines.append(f"Message: {error.get('message', 'No message')}")
        lines.append(f"Timestamp: {error.get('timestamp', datetime.now().isoformat())}")
        lines.append("")

        # Code Context
        if code_context:
            lines.append("CODE CONTEXT:")
            lines.append("-" * 70)
            lines.append(code_context)
            lines.append("-" * 70)
            lines.append("")

        # Stack Trace
        if error.get('stack_trace'):
            lines.append("STACK TRACE:")
            for i, frame in enumerate(error['stack_trace'][:5], 1):
                lines.append(f"{i}. at {frame['method']}")
                lines.append(f"   in {frame['file']}:{frame['line']}")
            lines.append("")

        # Knowledge Base Findings
        if similar_errors:
            lines.append("KNOWLEDGE BASE FINDINGS:")
            lines.append("Similar errors found in project history:")
            lines.append("")

            for i, case in enumerate(similar_errors[:3], 1):
                similarity = case.get('similarity', 0) * 100
                lines.append(f"{i}. [{case['date']}] Similarity: {similarity:.0f}%")

                if case.get('error_type'):
                    lines.append(f"   Error Type: {case['error_type']}")

                problem = case.get('problem', 'Unknown')
                lines.append(f"   Problem: {problem[:150]}...")

                if case.get('solution'):
                    solution = case['solution'][:200]
                    lines.append(f"   Solution: {solution}...")

                if case.get('fix'):
                    lines.append(f"   Fix Applied: {case['fix']}")

                if case.get('occurrences', 0) > 1:
                    lines.append(f"   ⚠️ Occurred {case['occurrences']} times")

                lines.append("")
        else:
            lines.append("KNOWLEDGE BASE FINDINGS:")
            lines.append("No similar errors found in project history.")
            lines.append("This appears to be a new error type.")
            lines.append("")

        # Pattern Analysis
        if pattern and pattern.get('is_recurring'):
            lines.append("⚠️ ERROR PATTERN DETECTED:")
            lines.append(f"This error has occurred {pattern['occurrences']} times")
            lines.append(f"First seen: {pattern.get('first_seen', 'Unknown')}")
            lines.append(f"Last seen: {pattern.get('last_seen', 'Unknown')}")
            lines.append(f"Trend: {pattern.get('trend', 'unknown').upper()}")
            lines.append(f"Severity: {pattern.get('severity', 'medium').upper()}")

            if pattern.get('frequency'):
                lines.append(f"Frequency: {pattern['frequency']}")

            lines.append("")
            lines.append("⚡ ROOT CAUSE ANALYSIS NEEDED:")
            lines.append("This is a recurring issue. Focus on identifying the underlying")
            lines.append("architectural or design problem causing repeated failures.")
            lines.append("")

        # Recent Changes
        if recent_changes:
            lines.append("RECENT CHANGES TO THIS FILE:")
            for i, change in enumerate(recent_changes[:3], 1):
                lines.append(f"{i}. {change['date']}")
                lines.append(f"   Query: {change['user_query'][:100]}...")
                if change.get('ai_action'):
                    lines.append(f"   Action: {change['ai_action'][:100]}...")
            lines.append("")

        # Expected vs Actual (for runtime errors)
        if error.get('severity') in ['exception', 'error']:
            lines.append("EXPECTED vs ACTUAL:")
            lines.append(f"Expected: The code should execute without errors")

            if error.get('method'):
                lines.append(f"          Method {error['method']} should complete normally")

            lines.append(f"Actual: {error.get('type', 'Error')} occurred")
            lines.append(f"        {error.get('message', 'Unknown error')}")
            lines.append("")

        # Investigation Request
        lines.append("=" * 70)
        lines.append("INVESTIGATION REQUEST:")
        lines.append("=" * 70)
        lines.append("")
        lines.append("Analyze this error using the project history and context above.")
        lines.append("Provide a comprehensive debugging report that includes:")
        lines.append("")
        lines.append("1. ROOT CAUSE:")
        lines.append("   - Why did this error occur?")
        lines.append("   - What is the underlying issue?")

        if recent_changes:
            lines.append("   - What changed recently that might have caused this?")

        lines.append("")
        lines.append("2. TIMELINE ANALYSIS:")
        lines.append("   - When did this error first appear?")

        if similar_errors:
            lines.append("   - How does it relate to past similar errors?")

        if pattern and pattern.get('is_recurring'):
            lines.append("   - Why does this error keep recurring?")

        lines.append("")
        lines.append("3. FIX:")
        lines.append("   - Exact code changes needed to resolve this error")
        lines.append("   - Line-by-line fix instructions")
        lines.append("   - Before and after code comparison")
        lines.append("")
        lines.append("4. PREVENTION:")
        lines.append("   - How to prevent this error pattern in the future")
        lines.append("   - Recommended code patterns or architecture changes")

        if pattern and pattern.get('is_recurring'):
            lines.append("   - Strategy to eliminate this recurring issue permanently")

        lines.append("")

        if similar_errors:
            lines.append("5. KNOWLEDGE BASE INTEGRATION:")
            lines.append("   - Cite specific past solutions when applicable")
            lines.append("   - Explain how this error relates to project history")
            lines.append("")

        lines.append("Respond with a clear, structured analysis that helps the developer")
        lines.append("understand and fix this error quickly.")

        return "\n".join(lines)

    def _pattern_alert_template(self,
                                error: Dict,
                                code_context: Optional[str],
                                similar_errors: Optional[List[Dict]],
                                pattern: Optional[Dict],
                                recent_changes: Optional[List[Dict]]) -> str:
        """
        Alert prompt for recurring error patterns.
        Use when pattern detection identifies a critical recurring issue.
        """
        lines = []

        lines.append("⚠️ RECURRING ERROR PATTERN ALERT")
        lines.append("=" * 70)
        lines.append("")

        if pattern:
            lines.append(f"Error Type: {error.get('type', 'Unknown')}")
            lines.append(f"Occurrences: {pattern['occurrences']} times")
            lines.append(f"Trend: {pattern.get('trend', 'unknown').upper()}")
            lines.append(f"Severity: {pattern.get('severity', 'medium').upper()}")
            lines.append("")

        lines.append("This error has occurred multiple times. This indicates a deeper")
        lines.append("architectural or design issue that needs permanent resolution.")
        lines.append("")

        # Include similar errors for context
        if similar_errors:
            lines.append("PAST OCCURRENCES:")
            for i, case in enumerate(similar_errors[:5], 1):
                lines.append(f"{i}. {case['date']} - {case.get('problem', 'Unknown')[:100]}")
            lines.append("")

        lines.append("CRITICAL ANALYSIS NEEDED:")
        lines.append("")
        lines.append("1. Identify the ROOT ARCHITECTURAL CAUSE")
        lines.append("   Why does this error keep happening?")
        lines.append("")
        lines.append("2. Design a PERMANENT FIX")
        lines.append("   Not just a workaround, but a structural solution")
        lines.append("")
        lines.append("3. Recommend REFACTORING STRATEGY")
        lines.append("   What code patterns should be changed project-wide?")
        lines.append("")

        return "\n".join(lines)

    def _quick_fix_template(self,
                           error: Dict,
                           code_context: Optional[str],
                           similar_errors: Optional[List[Dict]],
                           pattern: Optional[Dict],
                           recent_changes: Optional[List[Dict]]) -> str:
        """
        Quick fix prompt for known errors with existing solutions.
        Use when similar errors exist in Knowledge Base.
        """
        lines = []

        lines.append("🔧 QUICK FIX REQUESTED")
        lines.append("=" * 70)
        lines.append("")

        lines.append(f"Error: {error.get('type', 'Unknown')}")
        lines.append(f"File: {error.get('file_path', 'Unknown')}:{error.get('line', 0)}")
        lines.append(f"Message: {error.get('message', 'No message')}")
        lines.append("")

        if similar_errors and similar_errors[0].get('similarity', 0) > 0.8:
            best_match = similar_errors[0]
            lines.append("KNOWN SOLUTION FOUND:")
            lines.append(f"Date: {best_match['date']}")
            lines.append(f"Similarity: {best_match['similarity'] * 100:.0f}%")
            lines.append("")
            lines.append(f"Previous Problem: {best_match.get('problem', 'Unknown')}")
            lines.append("")
            lines.append(f"Solution Used: {best_match.get('solution', 'Unknown')}")
            lines.append("")

            if best_match.get('fix'):
                lines.append(f"Fix Applied: {best_match['fix']}")
                lines.append("")

        if code_context:
            lines.append("CURRENT CODE:")
            lines.append(code_context)
            lines.append("")

        lines.append("REQUEST:")
        lines.append("Provide the exact code fix needed, based on the past solution.")
        lines.append("Format: Show before/after code with clear line-by-line changes.")

        return "\n".join(lines)

    def format_solution_summary(self, solution: str, error: Dict) -> str:
        """
        Format AI solution for archiving to Knowledge Base.

        Args:
            solution: AI's full response
            error: Original error dict

        Returns:
            Formatted summary for error_solutions table
        """
        # Extract key parts from solution (first 500 chars is usually the summary)
        summary = solution[:500].strip()

        # Add metadata
        lines = [
            f"Error: {error.get('type', 'Unknown')} in {error.get('file_path', 'Unknown')}",
            f"Solved: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            summary,
            "",
            "Full solution archived in conversation history."
        ]

        return "\n".join(lines)


# Example usage and testing
if __name__ == "__main__":
    print("Debug Prompt Generator - Test Mode")
    print("=" * 70)
    print()

    generator = DebugPromptGenerator()

    # Test error
    test_error = {
        'type': 'NullReferenceException',
        'severity': 'exception',
        'message': 'Object reference not set to an instance of an object',
        'file_path': 'Assets/Scripts/PlayerController.cs',
        'line': 45,
        'method': 'Start()',
        'timestamp': datetime.now().isoformat(),
        'stack_trace': [
            {'method': 'PlayerController.Start()', 'file': 'Assets/Scripts/PlayerController.cs', 'line': 45},
            {'method': 'UnityEngine.MonoBehaviour.StartCoroutine()', 'file': 'UnityEngine.CoreModule.dll', 'line': 0}
        ]
    }

    # Test code context
    test_code_context = """    40 |     public InputSystem inputSystem;
    41 |     public PlayerData playerData;
    42 |
    43 |     void Start()
    44 |     {
 >>> 45 |         inputSystem = GetComponent<InputSystem>();
    46 |         playerData.Initialize();
    47 |     }
    48 |
    49 |     void Update()
    50 |     {"""

    # Test similar errors
    test_similar = [
        {
            'date': 'Jan 28',
            'similarity': 0.95,
            'error_type': 'NullReferenceException',
            'problem': 'NullRef in EnemyController.Start() - GetComponent<InputSystem> returned null',
            'solution': 'Changed to use InputManager.Instance singleton pattern',
            'fix': 'inputSystem = InputManager.Instance;',
            'occurrences': 1
        }
    ]

    # Test pattern
    test_pattern = {
        'occurrences': 3,
        'first_seen': 'Jan 26',
        'last_seen': 'Today',
        'trend': 'increasing',
        'frequency': '1.5 times/day',
        'is_recurring': True,
        'severity': 'high'
    }

    # Test recent changes
    test_changes = [
        {
            'date': 'Jan 30',
            'user_query': 'Update EnemyController to use new InputManager',
            'ai_action': 'Refactored EnemyController.Start() to use InputManager.Instance'
        }
    ]

    # Generate full investigation prompt
    print("FULL INVESTIGATION PROMPT:")
    print("=" * 70)
    prompt = generator.generate_debug_prompt(
        error=test_error,
        code_context=test_code_context,
        similar_errors=test_similar,
        pattern=test_pattern,
        recent_changes=test_changes,
        template='investigation'
    )
    print(prompt)
    print()
    print("=" * 70)
    print(f"Prompt length: {len(prompt)} characters")
