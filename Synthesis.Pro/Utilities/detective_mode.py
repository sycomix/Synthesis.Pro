"""
Detective Mode - Main Orchestrator
Part of Synthesis AI

Coordinates Unity log monitoring, Knowledge Base search, and AI debugging
to provide intelligent, context-aware error investigation and resolution.

Zero external dependencies - uses only Python standard library + internal modules.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import our detective components
from unity_log_detective import UnityLogDetective
from kb_detective import KnowledgeBaseDetective
from debug_prompt_generator import DebugPromptGenerator

# Import AI integration (optional - detective mode can work standalone)
try:
    from ai_chat_bridge import AIProvider, Config as AIConfig
    AI_INTEGRATION_AVAILABLE = True
except ImportError:
    AI_INTEGRATION_AVAILABLE = False

# Import Unity Console integration (optional)
try:
    from unity_console_reporter import UnityConsoleReporter
    UNITY_CONSOLE_AVAILABLE = True
except ImportError:
    UNITY_CONSOLE_AVAILABLE = False

# Import Performance Monitor (optional)
try:
    from performance_monitor import PerformanceMonitor
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

# Import AI Confidence Tracker (optional - Phase 4)
try:
    from ai_confidence_tracker import AIConfidenceTracker
    AI_CONFIDENCE_AVAILABLE = True
except ImportError:
    AI_CONFIDENCE_AVAILABLE = False


class DetectiveMode:
    """
    Main orchestrator for Detective Mode.
    Monitors Unity errors, searches Knowledge Base, generates AI prompts.
    """

    def __init__(self,
                 unity_log_path: Optional[str] = None,
                 kb_path: Optional[str] = None,
                 auto_investigate: bool = True,
                 auto_solve_with_ai: bool = False,
                 unity_console_integration: bool = True,
                 batch_mode: bool = False,
                 batch_window: float = 2.0,
                 enable_performance_monitoring: bool = False,
                 enable_ai_confidence_tracking: bool = False):
        """
        Initialize Detective Mode.

        Args:
            unity_log_path: Optional path to Unity Editor.log
            kb_path: Optional path to knowledge_base.db
            auto_investigate: If True, automatically investigate new errors
            auto_solve_with_ai: If True, automatically send prompts to AI and get solutions
            unity_console_integration: If True, send results to Unity console
            batch_mode: If True, collect and investigate multiple errors together
            batch_window: Time window in seconds to collect errors for batch processing
            enable_performance_monitoring: If True, track and report performance metrics (Phase 3)
            enable_ai_confidence_tracking: If True, track AI solution feedback and calculate confidence scores (Phase 4)
        """
        self.log_detective = UnityLogDetective(unity_log_path)
        self.kb_detective = KnowledgeBaseDetective(kb_path)
        self.prompt_generator = DebugPromptGenerator()

        self.auto_investigate = auto_investigate
        self.auto_solve_with_ai = auto_solve_with_ai
        self.batch_mode = batch_mode
        self.batch_window = batch_window
        self.investigation_history = []
        self.error_batch = []  # For batch mode
        self.last_error_time = None  # Track when last error arrived

        # Initialize Performance Monitor if enabled (Phase 3)
        self.performance_monitor = None
        if enable_performance_monitoring:
            if not PERFORMANCE_MONITOR_AVAILABLE:
                print("Warning: Performance monitoring not available (missing psutil)")
            else:
                try:
                    self.performance_monitor = PerformanceMonitor()
                    print("[OK] Performance monitoring enabled")
                except Exception as e:
                    print(f"Warning: Could not initialize Performance Monitor: {e}")
                    self.performance_monitor = None

        # Initialize Unity Console reporter if enabled
        self.unity_console = None
        if unity_console_integration:
            if not UNITY_CONSOLE_AVAILABLE:
                print("Warning: Unity Console integration not available")
            else:
                try:
                    self.unity_console = UnityConsoleReporter()
                    if self.unity_console.enabled:
                        print("[OK] Unity Console integration enabled")
                except Exception as e:
                    print(f"Warning: Could not initialize Unity Console: {e}")
                    self.unity_console = None

        # Initialize AI Confidence Tracker if enabled (Phase 4)
        self.confidence_tracker = None
        if enable_ai_confidence_tracking:
            if not AI_CONFIDENCE_AVAILABLE:
                print("Warning: AI Confidence Tracker not available")
            else:
                try:
                    self.confidence_tracker = AIConfidenceTracker(kb_path=kb_path)
                    print("[OK] AI Confidence Tracking enabled")
                except Exception as e:
                    print(f"Warning: Could not initialize AI Confidence Tracker: {e}")
                    self.confidence_tracker = None

        # Initialize AI provider if auto-solve is enabled
        self.ai_provider = None
        if auto_solve_with_ai:
            if not AI_INTEGRATION_AVAILABLE:
                print("Warning: AI integration not available (ai_chat_bridge.py issue)")
                print("         Detective mode will run without automatic AI solving")
                self.auto_solve_with_ai = False
            else:
                try:
                    ai_config = AIConfig()
                    self.ai_provider = AIProvider(ai_config)
                    print(f"[OK] AI Provider initialized: {ai_config.provider}")
                except Exception as e:
                    print(f"Warning: Could not initialize AI provider: {e}")
                    print("         Detective mode will run without automatic AI solving")
                    self.auto_solve_with_ai = False
                    self.ai_provider = None

        # Stats
        self.stats = {
            'errors_detected': 0,
            'investigations_run': 0,
            'solutions_archived': 0,
            'patterns_found': 0,
            'ai_solutions_generated': 0,
            'session_start': datetime.now().isoformat()
        }

    def watch_and_investigate(self, check_interval: float = 1.0, max_investigations: int = 0):
        """
        Watch Unity logs and automatically investigate errors.

        Args:
            check_interval: How often to check logs (seconds)
            max_investigations: Maximum investigations to run (0 = unlimited)
        """
        print("🔍 Detective Mode - Active")
        print("=" * 70)
        print(f"Monitoring: {self.log_detective.log_path}")
        print(f"Knowledge Base: {self.kb_detective.db_path}")
        print(f"Auto-investigate: {self.auto_investigate}")
        print(f"Auto-solve with AI: {self.auto_solve_with_ai}")
        if self.auto_solve_with_ai and self.ai_provider:
            print(f"AI Provider: {self.ai_provider.config.provider}")
        print(f"Unity Console: {'Enabled' if self.unity_console and self.unity_console.enabled else 'Disabled'}")
        print(f"Batch Mode: {'Enabled' if self.batch_mode else 'Disabled'}")
        if self.batch_mode:
            print(f"  Batch Window: {self.batch_window}s")
        print()

        if not os.path.exists(self.log_detective.log_path):
            print(f"⚠️ Warning: Unity log not found at {self.log_detective.log_path}")
            print("Detective Mode will wait for Unity to start...")
            print()

        investigations_run = 0

        try:
            while True:
                # Check for new errors
                if self.performance_monitor:
                    start_time = self.performance_monitor.start_timer('log_monitoring')

                result = self.log_detective.watch_log(check_interval)

                if self.performance_monitor:
                    self.performance_monitor.end_timer('log_monitoring', start_time)

                if result['status'] == 'errors_found':
                    self.stats['errors_detected'] += result['count']

                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚨 {result['count']} new error(s) detected!")
                    print()

                    # In batch mode, collect errors instead of investigating immediately
                    if self.batch_mode and self.auto_investigate:
                        for error in result['errors']:
                            print(f"⚠️  {error.get('type', 'Unknown')}: {error.get('message', 'No message')[:80]}")
                            if error.get('file_path') and error['file_path'] != 'Unknown':
                                print(f"    {error['file_path']}:{error.get('line', 0)}")

                            # Report error to Unity console
                            if self.unity_console:
                                self.unity_console.report_error_detected(error)

                            # Add to batch
                            self.error_batch.append(error)
                            self.last_error_time = time.time()

                        print(f"📦 Collected {len(self.error_batch)} error(s) in batch (waiting {self.batch_window}s for more...)")
                        print()
                    else:
                        # Standard mode - investigate each error individually
                        for error in result['errors']:
                            # Quick error summary
                            print(f"⚠️  {error.get('type', 'Unknown')}: {error.get('message', 'No message')[:80]}")

                            if error.get('file_path') and error['file_path'] != 'Unknown':
                                print(f"    {error['file_path']}:{error.get('line', 0)}")

                            # Report error to Unity console
                            if self.unity_console:
                                self.unity_console.report_error_detected(error)

                            # Auto-investigate if enabled
                            if self.auto_investigate:
                                print()
                                self.investigate_error(error)
                                investigations_run += 1

                                # Check if we've hit max investigations
                                if max_investigations > 0 and investigations_run >= max_investigations:
                                    print()
                                    print(f"✓ Completed {max_investigations} investigation(s)")
                                    return

                            print()

                # Check if batch is ready to process
                if self.batch_mode and self.error_batch and self.last_error_time:
                    time_since_last = time.time() - self.last_error_time
                    if time_since_last >= self.batch_window:
                        # Process the batch
                        investigations = self.investigate_batch(self.error_batch)
                        investigations_run += len(investigations)

                        # Clear the batch
                        self.error_batch = []
                        self.last_error_time = None

                        # Check if we've hit max investigations
                        if max_investigations > 0 and investigations_run >= max_investigations:
                            print()
                            print(f"✓ Completed {max_investigations} investigation(s)")
                            return

                elif result['status'] == 'error':
                    print(f"⚠️ Error: {result['message']}")
                    time.sleep(5)  # Wait before retrying

                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Detective Mode stopped by user")
            self.print_session_summary()

    def get_ai_solution(self, debug_prompt: str) -> Optional[str]:
        """
        Send debug prompt to AI and get solution.

        Args:
            debug_prompt: The investigation prompt to send to AI

        Returns:
            AI's solution or None if AI not available
        """
        if not self.ai_provider:
            return None

        try:
            print("   🤖 Sending to AI for analysis...")
            solution = self.ai_provider.call_ai(debug_prompt)
            self.stats['ai_solutions_generated'] += 1
            print("   ✓ AI solution received")
            return solution
        except Exception as e:
            print(f"   ⚠️ AI call failed: {e}")
            return None

    def investigate_error(self, error: Dict, template: str = 'investigation') -> Dict:
        """
        Perform comprehensive investigation of an error.

        Args:
            error: Error dict from UnityLogDetective
            template: Prompt template to use

        Returns:
            Investigation results dict
        """
        print("🔍 Starting investigation...")
        investigation_start = time.time()

        if self.performance_monitor:
            perf_start = self.performance_monitor.start_timer('investigation')

        # Report to Unity console
        if self.unity_console:
            self.unity_console.report_investigation_start(error)

        # Step 1: Extract code context
        code_context = None
        if error.get('file_path') and error['file_path'] != 'Unknown':
            if self.performance_monitor:
                code_start = self.performance_monitor.start_timer('code_context_extraction')

            code_context = self.log_detective.extract_code_context(
                error['file_path'],
                error.get('line', 0),
                context_lines=20
            )

            if self.performance_monitor:
                self.performance_monitor.end_timer('code_context_extraction', code_start)

            if code_context:
                print("   ✓ Code context extracted")
                if self.unity_console:
                    self.unity_console.report_investigation_progress("Code context extracted", "±20 lines around error")

        # Step 2: Search Knowledge Base for similar errors
        print("   🔍 Searching Knowledge Base...")

        if self.performance_monitor:
            kb_start = self.performance_monitor.start_timer('kb_search')

        similar_errors = self.kb_detective.search_similar_errors(error)

        if self.performance_monitor:
            self.performance_monitor.end_timer('kb_search', kb_start)
        if similar_errors:
            print(f"   ✓ Found {len(similar_errors)} similar case(s)")
            # Show top match
            top_match = similar_errors[0]
            print(f"      Best match: {top_match['similarity']:.0%} - {top_match['date']}")
            if self.unity_console:
                self.unity_console.report_similar_errors_found(similar_errors)
        else:
            print("   ℹ️ No similar errors found (new error type)")
            if self.unity_console:
                self.unity_console.report_similar_errors_found([])

        # Step 3: Check for error patterns
        print("   📊 Analyzing error patterns...")
        pattern = self.kb_detective.detect_error_pattern(error)
        if pattern and pattern.get('is_recurring'):
            self.stats['patterns_found'] += 1
            print(f"   ⚠️ RECURRING PATTERN: {pattern['occurrences']} occurrences")
            print(f"      Trend: {pattern.get('trend', 'unknown')}")
            if self.unity_console:
                self.unity_console.report_pattern_detected(pattern)
            # Use pattern alert template for recurring errors
            if template == 'investigation':
                template = 'pattern_alert'
        else:
            print("   ✓ No recurring pattern detected")

        # Step 4: Get recent changes to the file
        recent_changes = []
        if error.get('file_path') and error['file_path'] != 'Unknown':
            recent_changes = self.kb_detective.get_recent_changes(error['file_path'])
            if recent_changes:
                print(f"   📝 Found {len(recent_changes)} recent change(s) to this file")

        # Step 5: Generate AI debugging prompt
        print("   ✍️ Generating debug prompt...")
        debug_prompt = self.prompt_generator.generate_debug_prompt(
            error=error,
            code_context=code_context,
            similar_errors=similar_errors,
            pattern=pattern,
            recent_changes=recent_changes,
            template=template
        )

        investigation_time = time.time() - investigation_start
        self.stats['investigations_run'] += 1

        if self.performance_monitor:
            self.performance_monitor.end_timer('investigation', perf_start)

        print(f"   ✓ Investigation complete ({investigation_time:.2f}s)")

        # Report investigation complete to Unity
        if self.unity_console:
            self.unity_console.report_investigation_complete(investigation_time)

        print()

        # Prepare investigation result
        investigation = {
            'error': error,
            'code_context': code_context,
            'similar_errors': similar_errors,
            'pattern': pattern,
            'recent_changes': recent_changes,
            'debug_prompt': debug_prompt,
            'investigation_time': investigation_time,
            'timestamp': datetime.now().isoformat(),
            'ai_solution': None
        }

        # Get AI solution if auto-solve is enabled
        if self.auto_solve_with_ai and self.ai_provider:
            # Check AI confidence before getting solution (Phase 4)
            if self.confidence_tracker:
                error_type = error.get('type', 'Unknown')
                should_warn, warning_msg = self.confidence_tracker.should_warn_user(error_type)
                if should_warn:
                    print()
                    print("   ⚠️ " + warning_msg)
                    print()

                    # Report confidence warning to Unity console
                    if self.unity_console:
                        score_data = self.confidence_tracker.get_confidence_score(error_type)
                        self.unity_console.report_ai_confidence_warning(
                            error_type=error_type,
                            confidence_score=score_data['confidence_score'],
                            success_rate=score_data.get('success_rate', 0.0),
                            recommendation=score_data['recommendation']
                        )

            ai_solution = self.get_ai_solution(debug_prompt)
            if ai_solution:
                investigation['ai_solution'] = ai_solution

                # Report AI solution to Unity console
                if self.unity_console:
                    self.unity_console.report_ai_solution(error, ai_solution)

                # Automatically archive the solution
                print("   💾 Archiving solution to Knowledge Base...")
                solution_id = self.archive_solution(error, ai_solution)
                if solution_id:
                    print("   ✓ Solution archived for future reference")
                    investigation['solution_id'] = solution_id
                    if self.unity_console:
                        self.unity_console.report_solution_archived()
                print()

        self.investigation_history.append(investigation)

        # Display the prompt
        print("=" * 70)
        print("DEBUG PROMPT READY FOR AI:")
        print("=" * 70)
        print()
        print(debug_prompt)
        print()
        print("=" * 70)

        # Display AI solution if available
        if investigation['ai_solution']:
            print()
            print("=" * 70)
            print("🤖 AI SOLUTION:")
            print("=" * 70)
            print()
            print(investigation['ai_solution'])
            print()
            print("=" * 70)

            # Collect feedback if confidence tracking enabled (Phase 4)
            if self.confidence_tracker:
                print()
                self._collect_solution_feedback(investigation, error)

        print()

        return investigation

    def _collect_solution_feedback(self, investigation: Dict, error: Dict):
        """
        Collect feedback on AI solution effectiveness (Phase 4).

        Args:
            investigation: Investigation dict containing AI solution
            error: Error dict
        """
        print("📊 AI Solution Feedback (Phase 4 - AI Confidence Tracking)")
        print("-" * 70)
        print("Did this AI solution work?")
        print("  1) ✓ Worked - Solution fixed the problem")
        print("  2) ~ Partial - Solution helped but didn't fully solve it")
        print("  3) ✗ Failed - Solution didn't work")
        print("  4) ⚠️ Hallucination - AI suggested non-existent APIs or wrong approach")
        print("  5) N/A - Haven't tried it yet / Not applicable")
        print("  6) Skip - Don't provide feedback now")
        print()

        try:
            choice = input("Enter choice (1-6): ").strip()

            feedback_map = {
                '1': 'worked',
                '2': 'partial',
                '3': 'failed',
                '4': 'hallucinated',
                '5': 'not_applicable',
                '6': None  # Skip
            }

            feedback_type = feedback_map.get(choice)

            if feedback_type is None:
                print("Feedback skipped.")
                return

            # Collect additional details for failures and hallucinations
            failure_reason = None
            hallucination_type = None
            user_notes = None

            if feedback_type == 'failed':
                print()
                print("Why did it fail?")
                print("  1) API doesn't exist in my Unity version")
                print("  2) Wrong namespace or using statement")
                print("  3) Logic error in suggested code")
                print("  4) Doesn't address the root cause")
                print("  5) Other")
                reason_choice = input("Enter choice (1-5, or press Enter to skip): ").strip()

                reason_map = {
                    '1': 'version_incompatible',
                    '2': 'wrong_namespace',
                    '3': 'logic_error',
                    '4': 'wrong_approach',
                    '5': 'other'
                }
                failure_reason = reason_map.get(reason_choice, 'unspecified')

            elif feedback_type == 'hallucinated':
                print()
                print("What did AI hallucinate?")
                print("  1) Suggested an API that doesn't exist")
                print("  2) Wrong namespace or class")
                print("  3) Deprecated method (removed in current Unity version)")
                print("  4) Made up a feature that doesn't exist")
                print("  5) Other")
                halluc_choice = input("Enter choice (1-5, or press Enter to skip): ").strip()

                halluc_map = {
                    '1': 'nonexistent_api',
                    '2': 'wrong_namespace',
                    '3': 'deprecated_method',
                    '4': 'fictional_feature',
                    '5': 'other'
                }
                hallucination_type = halluc_map.get(halluc_choice, 'unspecified')

            # Optional notes
            print()
            user_notes = input("Any additional notes? (optional, press Enter to skip): ").strip()
            if not user_notes:
                user_notes = None

            # Record feedback
            solution_id = investigation.get('solution_id')
            self.confidence_tracker.record_feedback(
                solution_id=solution_id,
                error_type=error.get('type', 'Unknown'),
                feedback_type=feedback_type,
                error_message=error.get('message'),
                file_path=error.get('file_path'),
                failure_reason=failure_reason,
                hallucination_type=hallucination_type,
                user_notes=user_notes,
                ai_provider=self.ai_provider.config.provider if self.ai_provider else None
            )

            print()
            print("✓ Feedback recorded! This helps improve AI accuracy for future errors.")
            print()

        except (KeyboardInterrupt, EOFError):
            print()
            print("Feedback cancelled.")
            print()

    def group_similar_errors(self, errors: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group similar errors together for batch processing.

        Args:
            errors: List of error dicts

        Returns:
            Dict mapping group keys to lists of errors
        """
        groups = {}
        for error in errors:
            # Group by error type and file path
            error_type = error.get('type', 'Unknown')
            file_path = error.get('file_path', 'Unknown')
            group_key = f"{error_type}:{file_path}"

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(error)

        return groups

    def investigate_batch(self, errors: List[Dict]) -> List[Dict]:
        """
        Investigate multiple errors together in batch mode.

        Args:
            errors: List of error dicts to investigate

        Returns:
            List of investigation results
        """
        if not errors:
            return []

        print(f"\n🔍 Batch Investigation - Processing {len(errors)} error(s)")
        print("=" * 70)

        # Group similar errors
        groups = self.group_similar_errors(errors)
        print(f"Grouped into {len(groups)} error group(s)")
        print()

        investigations = []

        for group_key, group_errors in groups.items():
            error_type, file_path = group_key.split(':', 1)
            count = len(group_errors)

            print(f"📦 Group: {error_type} in {file_path} ({count} occurrence(s))")

            # Investigate the first error in the group (representative)
            primary_error = group_errors[0]

            # Report to Unity console
            if self.unity_console:
                self.unity_console.send_log(
                    f"[DETECTIVE MODE] Batch Investigation\n"
                    f"Processing {count} {error_type} error(s) in {file_path}",
                    "log"
                )

            # Run investigation on primary error
            investigation = self.investigate_error(primary_error)

            # Add info about other occurrences
            if count > 1:
                investigation['batch_info'] = {
                    'total_occurrences': count,
                    'error_lines': [e.get('line', 0) for e in group_errors],
                    'grouped': True
                }
                print(f"   ℹ️  Found {count-1} more occurrence(s) at lines: {investigation['batch_info']['error_lines'][1:]}")

            investigations.append(investigation)
            print()

        print("=" * 70)
        print(f"✓ Batch investigation complete - {len(investigations)} group(s) processed")
        print()

        return investigations

    def archive_solution(self, error: Dict, solution: str, fix_code: Optional[str] = None) -> Optional[int]:
        """
        Archive a solved error to Knowledge Base.

        Args:
            error: Error dict
            solution: AI's solution explanation
            fix_code: Optional code that fixed the error

        Returns:
            Solution ID if successfully archived, None otherwise
        """
        solution_id = self.kb_detective.archive_solution(error, solution, fix_code)
        if solution_id:
            self.stats['solutions_archived'] += 1
            print("✓ Solution archived to Knowledge Base")
        return solution_id

    def get_investigation_history(self, count: int = 5) -> List[Dict]:
        """
        Get recent investigation history.

        Args:
            count: Number of recent investigations to return

        Returns:
            List of investigation dicts
        """
        return self.investigation_history[-count:]

    def print_session_summary(self):
        """Print summary of current Detective Mode session."""
        print()
        print("=" * 70)
        print("DETECTIVE MODE - SESSION SUMMARY")
        print("=" * 70)
        print()
        print(f"Session started: {self.stats['session_start']}")
        print(f"Errors detected: {self.stats['errors_detected']}")
        print(f"Investigations run: {self.stats['investigations_run']}")
        print(f"Patterns found: {self.stats['patterns_found']}")
        print(f"AI solutions generated: {self.stats['ai_solutions_generated']}")
        print(f"Solutions archived: {self.stats['solutions_archived']}")
        print()

        if self.investigation_history:
            print(f"Recent investigations ({len(self.investigation_history)}):")
            for i, inv in enumerate(self.investigation_history[-5:], 1):
                error = inv['error']
                print(f"{i}. {error.get('type', 'Unknown')} in {Path(error.get('file_path', 'Unknown')).name}")
                print(f"   Time: {inv['investigation_time']:.2f}s")

                if inv.get('similar_errors'):
                    print(f"   Similar cases: {len(inv['similar_errors'])}")

                if inv.get('pattern') and inv['pattern'].get('is_recurring'):
                    print(f"   ⚠️ Recurring pattern detected")

        print()

        # Performance report (Phase 3)
        if self.performance_monitor:
            print()
            print(self.performance_monitor.get_performance_report())
            print()

    def export_investigation(self, investigation: Dict, output_path: str) -> bool:
        """
        Export investigation to JSON file.

        Args:
            investigation: Investigation dict
            output_path: Where to save JSON file

        Returns:
            True if successful
        """
        try:
            # Remove non-serializable parts
            export_data = {
                'error': investigation['error'],
                'similar_errors': investigation.get('similar_errors', []),
                'pattern': investigation.get('pattern'),
                'recent_changes': investigation.get('recent_changes', []),
                'debug_prompt': investigation['debug_prompt'],
                'investigation_time': investigation['investigation_time'],
                'timestamp': investigation['timestamp']
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error exporting investigation: {e}")
            return False


# CLI Interface
def main():
    """Main entry point for Detective Mode CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Synthesis AI - Detective Mode',
        epilog='Monitor Unity errors and get AI-powered debugging assistance'
    )

    parser.add_argument(
        '--log-path',
        help='Path to Unity Editor.log (auto-detected if not specified)',
        default=None
    )

    parser.add_argument(
        '--kb-path',
        help='Path to knowledge_base.db (auto-detected if not specified)',
        default=None
    )

    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Log check interval in seconds (default: 1.0)'
    )

    parser.add_argument(
        '--max-investigations',
        type=int,
        default=0,
        help='Maximum number of investigations to run (0 = unlimited)'
    )

    parser.add_argument(
        '--no-auto',
        action='store_true',
        help='Disable automatic investigation (just monitor)'
    )

    parser.add_argument(
        '--auto-solve',
        action='store_true',
        help='Automatically send debug prompts to AI and get solutions (Phase 3)'
    )

    parser.add_argument(
        '--no-unity-console',
        action='store_true',
        help='Disable Unity console integration (Phase 3)'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Enable batch mode - collect and investigate multiple errors together (Phase 3)'
    )

    parser.add_argument(
        '--batch-window',
        type=float,
        default=2.0,
        help='Time window in seconds to collect errors for batch processing (default: 2.0)'
    )

    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Show error trend analysis dashboard and exit (Phase 3)'
    )

    parser.add_argument(
        '--dashboard-days',
        type=int,
        default=30,
        help='Number of days for dashboard analysis (default: 30)'
    )

    parser.add_argument(
        '--performance',
        action='store_true',
        help='Enable performance monitoring and reporting (Phase 3)'
    )

    parser.add_argument(
        '--confidence-tracking',
        action='store_true',
        help='Enable AI confidence tracking - monitors AI solution accuracy (Phase 4)'
    )

    parser.add_argument(
        '--confidence-report',
        action='store_true',
        help='Show AI confidence report and exit (Phase 4)'
    )

    parser.add_argument(
        '--confidence-days',
        type=int,
        default=30,
        help='Number of days for confidence analysis (default: 30)'
    )

    parser.add_argument(
        '--export-shareable',
        type=str,
        metavar='FILE',
        help='Export anonymized community insights to JSON file (Phase 4 - Privacy Safe)'
    )

    parser.add_argument(
        '--export-personal',
        type=str,
        metavar='FILE',
        help='Export personal backup to JSON file (Phase 4 - PRIVATE, local backup only)'
    )

    parser.add_argument(
        '--export-solutions',
        type=str,
        metavar='FILE',
        help='Export anonymized solutions from Knowledge Base (Phase 4 - Privacy Safe)'
    )

    parser.add_argument(
        '--export-days',
        type=int,
        default=90,
        help='Number of days for data export (default: 90)'
    )

    args = parser.parse_args()

    # If dashboard mode, show dashboard and exit
    if args.dashboard:
        try:
            from error_trend_dashboard import ErrorTrendDashboard
            dashboard = ErrorTrendDashboard(kb_path=args.kb_path)
            report = dashboard.generate_dashboard(days=args.dashboard_days)
            print(report)
            return
        except ImportError:
            print("Error: error_trend_dashboard module not found")
            return
        except Exception as e:
            print(f"Error generating dashboard: {e}")
            return

    # If confidence report mode, show report and exit (Phase 4)
    if args.confidence_report:
        try:
            from ai_confidence_tracker import AIConfidenceTracker
            tracker = AIConfidenceTracker(kb_path=args.kb_path)
            report = tracker.generate_confidence_report(days=args.confidence_days)
            print(report)
            return
        except ImportError:
            print("Error: ai_confidence_tracker module not found")
            return
        except Exception as e:
            print(f"Error generating confidence report: {e}")
            return

    # If export shareable mode, export anonymized insights and exit (Phase 4)
    if args.export_shareable:
        try:
            import json
            from ai_confidence_tracker import AIConfidenceTracker
            tracker = AIConfidenceTracker(kb_path=args.kb_path)
            insights = tracker.export_shareable_insights(days=args.export_days)

            with open(args.export_shareable, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2)

            print("=" * 70)
            print("SHAREABLE INSIGHTS EXPORTED")
            print("=" * 70)
            print(f"File: {args.export_shareable}")
            print(f"Privacy: Anonymized - no project-specific data")
            print(f"Error types: {len(insights['error_type_confidence'])}")
            print(f"Hallucination patterns: {len(insights['hallucination_patterns'])}")
            print(f"Providers: {len(insights['provider_performance'])}")
            print()
            print("This file is SAFE to share with the community!")
            print("=" * 70)
            return
        except ImportError:
            print("Error: ai_confidence_tracker module not found")
            return
        except Exception as e:
            print(f"Error exporting shareable insights: {e}")
            return

    # If export personal mode, export full backup and exit (Phase 4)
    if args.export_personal:
        try:
            import json
            from ai_confidence_tracker import AIConfidenceTracker
            tracker = AIConfidenceTracker(kb_path=args.kb_path)
            backup = tracker.export_personal_backup()

            with open(args.export_personal, 'w', encoding='utf-8') as f:
                json.dump(backup, f, indent=2)

            print("=" * 70)
            print("PERSONAL BACKUP EXPORTED")
            print("=" * 70)
            print(f"File: {args.export_personal}")
            print(f"Privacy: CONTAINS YOUR PROJECT DATA")
            print(f"Records: {backup['record_count']}")
            print()
            print("⚠️  WARNING: This file contains:")
            print("   - Your file paths")
            print("   - Your notes")
            print("   - Your error messages")
            print("   - Project-specific data")
            print()
            print("   FOR LOCAL BACKUP ONLY - DO NOT UPLOAD!")
            print("=" * 70)
            return
        except ImportError:
            print("Error: ai_confidence_tracker module not found")
            return
        except Exception as e:
            print(f"Error exporting personal backup: {e}")
            return

    # If export solutions mode, export anonymized KB solutions and exit (Phase 4)
    if args.export_solutions:
        try:
            import json
            from kb_detective import KnowledgeBaseDetective
            kb = KnowledgeBaseDetective(kb_path=args.kb_path)
            solutions = kb.export_anonymized_solutions(days=args.export_days)

            with open(args.export_solutions, 'w', encoding='utf-8') as f:
                json.dump(solutions, f, indent=2)

            print("=" * 70)
            print("ANONYMIZED SOLUTIONS EXPORTED")
            print("=" * 70)
            print(f"File: {args.export_solutions}")
            print(f"Privacy: Anonymized - no NightBlade/project-specific data")
            print(f"Solutions: {len(solutions)}")
            print()
            print("✓ Project-specific details stripped:")
            print("   - File paths removed")
            print("   - Variable names generalized")
            print("   - Class names anonymized")
            print("   - Only debugging patterns kept")
            print()
            print("This file is SAFE to share with the community!")
            print("=" * 70)
            return
        except ImportError:
            print("Error: kb_detective module not found")
            return
        except Exception as e:
            print(f"Error exporting anonymized solutions: {e}")
            return

    # Initialize Detective Mode
    detective = DetectiveMode(
        unity_log_path=args.log_path,
        kb_path=args.kb_path,
        auto_investigate=not args.no_auto,
        auto_solve_with_ai=args.auto_solve,
        unity_console_integration=not args.no_unity_console,
        batch_mode=args.batch,
        batch_window=args.batch_window,
        enable_performance_monitoring=args.performance,
        enable_ai_confidence_tracking=args.confidence_tracking
    )

    # Start watching
    detective.watch_and_investigate(
        check_interval=args.interval,
        max_investigations=args.max_investigations
    )


# Example usage and testing
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        main()
    else:
        # Test mode
        print("Detective Mode - Test Mode")
        print("=" * 70)
        print()

        detective = DetectiveMode(auto_investigate=True)

        # Test with sample error
        test_error = {
            'type': 'NullReferenceException',
            'severity': 'exception',
            'message': 'Object reference not set to an instance of an object',
            'file_path': 'Assets/Scripts/PlayerController.cs',
            'line': 45,
            'method': 'Start()',
            'timestamp': datetime.now().isoformat(),
            'stack_trace': [
                {
                    'method': 'PlayerController.Start()',
                    'file': 'Assets/Scripts/PlayerController.cs',
                    'line': 45
                }
            ]
        }

        print("Testing investigation workflow...")
        print()

        investigation = detective.investigate_error(test_error)

        print()
        print("Investigation complete!")
        print()

        # Test solution archiving
        print("Testing solution archiving...")
        solution = "The issue is caused by GetComponent<InputSystem>() returning null. The InputSystem component was removed from the project. Change to use InputManager.Instance singleton pattern."
        fix_code = "inputSystem = InputManager.Instance;"

        success = detective.archive_solution(test_error, solution, fix_code)
        print(f"Archive result: {success}")
        print()

        detective.print_session_summary()
