"""
Unity Console Reporter for Detective Mode
Sends investigation results to Unity's console in real-time via HTTP
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime


class UnityConsoleReporter:
    """
    Reports detective mode investigations to Unity's console.
    Uses the existing SynLink HTTP server on port 9765.
    """

    def __init__(self, unity_http_port: int = 9765):
        """
        Initialize Unity Console Reporter.

        Args:
            unity_http_port: Port for Unity's HTTP server (default: 9765)
        """
        self.unity_http_port = unity_http_port
        self.base_url = f"http://localhost:{unity_http_port}/"
        self.enabled = True
        self.test_connection()

    def test_connection(self) -> bool:
        """
        Test connection to Unity HTTP server.

        Returns:
            True if connected, False otherwise
        """
        try:
            response = requests.post(
                self.base_url,
                json={"command": "ping"},
                timeout=2
            )
            if response.status_code == 200:
                return True
            else:
                print(f"[UnityConsole] Warning: Unity HTTP server responded with status {response.status_code}")
                self.enabled = False
                return False
        except requests.exceptions.ConnectionError:
            print(f"[UnityConsole] Warning: Cannot connect to Unity on port {self.unity_http_port}")
            print(f"[UnityConsole] Unity console reporting disabled (detective mode will still work)")
            self.enabled = False
            return False
        except Exception as e:
            print(f"[UnityConsole] Warning: Connection test failed: {e}")
            self.enabled = False
            return False

    def send_log(self, message: str, log_type: str = "log") -> bool:
        """
        Send a log message to Unity console.

        Args:
            message: Message to log
            log_type: Type of log (log, warning, error)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            response = requests.post(
                self.base_url,
                json={
                    "command": "log",
                    "args": {
                        "message": message,
                        "type": log_type
                    }
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            # Silently fail - don't spam console if Unity disconnects
            return False

    def report_error_detected(self, error: Dict) -> bool:
        """
        Report that an error was detected.

        Args:
            error: Error dictionary from UnityLogDetective

        Returns:
            True if successful
        """
        error_type = error.get('type', 'Unknown')
        message = error.get('message', 'No message')
        file_path = error.get('file_path', 'Unknown')
        line = error.get('line', 0)

        log_message = (
            f"[DETECTIVE MODE] Error Detected!\n"
            f"Type: {error_type}\n"
            f"Message: {message}\n"
            f"Location: {file_path}:{line}"
        )

        return self.send_log(log_message, "warning")

    def report_investigation_start(self, error: Dict) -> bool:
        """
        Report that investigation has started.

        Args:
            error: Error dictionary

        Returns:
            True if successful
        """
        error_type = error.get('type', 'Unknown')
        file_path = error.get('file_path', 'Unknown')

        log_message = (
            f"[DETECTIVE MODE] Investigation Started\n"
            f"Investigating: {error_type} in {file_path}\n"
            f"Searching Knowledge Base for similar errors..."
        )

        return self.send_log(log_message, "log")

    def report_investigation_progress(self, step: str, details: str = "") -> bool:
        """
        Report investigation progress.

        Args:
            step: Step name (e.g., "Code context extracted")
            details: Optional details about the step

        Returns:
            True if successful
        """
        log_message = f"[DETECTIVE MODE] {step}"
        if details:
            log_message += f"\n{details}"

        return self.send_log(log_message, "log")

    def report_pattern_detected(self, pattern: Dict) -> bool:
        """
        Report that a recurring pattern was detected.

        Args:
            pattern: Pattern dictionary from KnowledgeBaseDetective

        Returns:
            True if successful
        """
        occurrences = pattern.get('occurrences', 0)
        trend = pattern.get('trend', 'unknown')

        log_message = (
            f"[DETECTIVE MODE] RECURRING PATTERN DETECTED!\n"
            f"This error has occurred {occurrences} times\n"
            f"Trend: {trend.upper()}\n"
            f"This indicates a systemic issue that needs attention!"
        )

        return self.send_log(log_message, "warning")

    def report_similar_errors_found(self, similar_errors: list) -> bool:
        """
        Report similar errors found in Knowledge Base.

        Args:
            similar_errors: List of similar error dicts

        Returns:
            True if successful
        """
        count = len(similar_errors)

        if count == 0:
            log_message = "[DETECTIVE MODE] No similar errors found (new error type)"
        else:
            log_message = f"[DETECTIVE MODE] Found {count} similar case(s) in Knowledge Base\n"

            # Show top match
            top_match = similar_errors[0]
            similarity = top_match.get('similarity', 0)
            date = top_match.get('date', 'Unknown')
            problem = top_match.get('problem', 'No description')[:100]

            log_message += f"Best match: {similarity:.0%} similarity from {date}\n"
            log_message += f"Problem: {problem}"

        return self.send_log(log_message, "log")

    def report_investigation_complete(self, investigation_time: float) -> bool:
        """
        Report that investigation is complete.

        Args:
            investigation_time: Time taken in seconds

        Returns:
            True if successful
        """
        log_message = f"[DETECTIVE MODE] Investigation complete ({investigation_time:.2f}s)"
        return self.send_log(log_message, "log")

    def report_ai_solution(self, error: Dict, solution: str) -> bool:
        """
        Report AI solution to Unity console.

        Args:
            error: Error dictionary
            solution: AI's solution text

        Returns:
            True if successful
        """
        error_type = error.get('type', 'Unknown')
        file_path = error.get('file_path', 'Unknown')

        # Truncate solution if too long (Unity console has limits)
        max_length = 1000
        if len(solution) > max_length:
            solution_preview = solution[:max_length] + "\n...(truncated, see Python console for full solution)"
        else:
            solution_preview = solution

        log_message = (
            f"[DETECTIVE MODE] AI Solution Received\n"
            f"For: {error_type} in {file_path}\n"
            f"---\n"
            f"{solution_preview}"
        )

        return self.send_log(log_message, "log")

    def report_solution_archived(self) -> bool:
        """
        Report that solution was archived to Knowledge Base.

        Returns:
            True if successful
        """
        log_message = "[DETECTIVE MODE] Solution archived to Knowledge Base for future reference"
        return self.send_log(log_message, "log")

    def report_ai_confidence_warning(self, error_type: str, confidence_score: float, success_rate: float, recommendation: str) -> bool:
        """
        Report AI confidence warning to Unity console (Phase 4).

        Args:
            error_type: Type of error
            confidence_score: Confidence score (0.0-1.0)
            success_rate: Success rate (0.0-1.0)
            recommendation: Recommendation text

        Returns:
            True if successful
        """
        log_message = (
            f"[DETECTIVE MODE - AI CONFIDENCE WARNING]\n"
            f"Error Type: {error_type}\n"
            f"AI Success Rate: {success_rate*100:.0f}%\n"
            f"Confidence Score: {confidence_score*100:.0f}%\n"
            f"Recommendation: {recommendation}"
        )

        return self.send_log(log_message, "warning")

    def report_session_summary(self, stats: Dict) -> bool:
        """
        Report session summary statistics.

        Args:
            stats: Statistics dictionary

        Returns:
            True if successful
        """
        log_message = (
            f"[DETECTIVE MODE] Session Summary\n"
            f"Errors detected: {stats.get('errors_detected', 0)}\n"
            f"Investigations run: {stats.get('investigations_run', 0)}\n"
            f"AI solutions generated: {stats.get('ai_solutions_generated', 0)}\n"
            f"Solutions archived: {stats.get('solutions_archived', 0)}\n"
            f"Patterns found: {stats.get('patterns_found', 0)}"
        )

        return self.send_log(log_message, "log")

    def report_error(self, error_message: str) -> bool:
        """
        Report an error in detective mode itself.

        Args:
            error_message: Error message

        Returns:
            True if successful
        """
        log_message = f"[DETECTIVE MODE] Error: {error_message}"
        return self.send_log(log_message, "error")


# Convenience function for testing
def test_unity_console_reporter():
    """Test Unity Console Reporter"""
    print("Testing Unity Console Reporter...")

    reporter = UnityConsoleReporter()

    if not reporter.enabled:
        print("Unity not connected - cannot test")
        return

    # Test error detection report
    test_error = {
        'type': 'NullReferenceException',
        'message': 'Object reference not set to an instance of an object',
        'file_path': 'Assets/Scripts/TestScript.cs',
        'line': 42
    }

    reporter.report_error_detected(test_error)
    reporter.report_investigation_start(test_error)
    reporter.report_investigation_progress("Code context extracted", "20 lines around error")
    reporter.report_similar_errors_found([
        {
            'similarity': 0.95,
            'date': 'Jan 30',
            'problem': 'Similar NullRef in EnemyController'
        }
    ])
    reporter.report_investigation_complete(0.85)

    print("Test messages sent to Unity console!")


if __name__ == "__main__":
    test_unity_console_reporter()
