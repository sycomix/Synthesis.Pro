"""
Unity Log Detective - Real-time Unity error monitoring and analysis
Part of Synthesis AI Detective Mode

Monitors Unity's Editor.log for errors, parses stack traces, and prepares
structured error reports for AI debugging assistance.

Zero external dependencies - uses only Python standard library.
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class UnityLogDetective:
    """
    Monitors Unity Editor.log and detects errors in real-time.
    Extracts structured error information for intelligent debugging.
    """

    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize the detective.

        Args:
            log_path: Optional path to Editor.log. If None, auto-detects.
        """
        self.log_path = log_path or self._find_unity_log()
        self.last_position = 0
        self.detected_errors = []

        # Code context cache (Phase 3 Performance Optimization)
        # Cache key: (file_path, line, context_lines) -> cached context
        self._code_context_cache = {}
        self._cache_max_size = 50  # Limit cache to 50 entries

        # Regex patterns for error detection
        self.patterns = {
            # C# compiler errors: Assets/Script.cs(45,10): error CS0246: message
            'compiler_error': re.compile(
                r'^(.*?)\((\d+),(\d+)\):\s*error\s+([^:]+):\s*(.*)$',
                re.MULTILINE
            ),

            # Runtime exceptions: NullReferenceException: message
            'exception': re.compile(
                r'^([A-Za-z][A-Za-z0-9.]*Exception):\s*(.*)$',
                re.MULTILINE
            ),

            # Stack trace lines: at ClassName.MethodName () [0x00001] in /path/file.cs:45
            'stack_trace': re.compile(
                r'^\s*at\s+(.*?)\s+\[0x[0-9a-fA-F]+\]\s+in\s+(.*?):(\d+)\s*$',
                re.MULTILINE
            ),

            # Unity assertions: Assertion failed: message
            'assertion': re.compile(
                r'^Assertion\s+failed:\s*(.*)$',
                re.MULTILINE
            ),

            # Unity warnings: warning: message
            'warning': re.compile(
                r'^.*?warning:\s*(.*)$',
                re.MULTILINE | re.IGNORECASE
            )
        }

    def _find_unity_log(self) -> str:
        """
        Auto-detect Unity Editor.log location based on OS.

        Returns:
            Path to Editor.log
        """
        if os.name == 'nt':  # Windows
            # Try common Windows locations
            appdata = os.getenv('APPDATA')
            if appdata:
                # Unity 2021+
                log_path = Path(appdata).parent / 'Local' / 'Unity' / 'Editor' / 'Editor.log'
                if log_path.exists():
                    return str(log_path)

            # Unity 2020 and earlier
            local_appdata = os.getenv('LOCALAPPDATA')
            if local_appdata:
                log_path = Path(local_appdata) / 'Unity' / 'Editor' / 'Editor.log'
                if log_path.exists():
                    return str(log_path)

        elif os.name == 'posix':  # macOS/Linux
            home = Path.home()

            # macOS
            log_path = home / 'Library' / 'Logs' / 'Unity' / 'Editor.log'
            if log_path.exists():
                return str(log_path)

            # Linux
            log_path = home / '.config' / 'unity3d' / 'Editor.log'
            if log_path.exists():
                return str(log_path)

        # Fallback - return empty string, will be caught later
        return ""

    def watch_log(self, check_interval: float = 1.0) -> Dict:
        """
        Check for new errors in the log file.

        Args:
            check_interval: How often to check (seconds)

        Returns:
            Dict containing any new errors found
        """
        if not self.log_path or not os.path.exists(self.log_path):
            return {
                'status': 'error',
                'message': f'Unity log not found at: {self.log_path}',
                'errors': []
            }

        try:
            # Get current file size
            file_size = os.path.getsize(self.log_path)

            # If file was truncated (Unity restart), reset position
            if file_size < self.last_position:
                self.last_position = 0

            # Only read new content
            if file_size > self.last_position:
                with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_position)
                    new_content = f.read()
                    self.last_position = f.tell()

                    # Parse new errors
                    errors = self._parse_errors(new_content)

                    if errors:
                        self.detected_errors.extend(errors)
                        return {
                            'status': 'errors_found',
                            'count': len(errors),
                            'errors': errors
                        }

            return {
                'status': 'no_new_errors',
                'errors': []
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to read log: {str(e)}',
                'errors': []
            }

    def _parse_errors(self, content: str) -> List[Dict]:
        """
        Parse error information from log content.

        Args:
            content: Raw log content to parse

        Returns:
            List of structured error dictionaries
        """
        errors = []

        # Find all compiler errors
        for match in self.patterns['compiler_error'].finditer(content):
            errors.append({
                'type': 'CompilerError',
                'severity': 'error',
                'file_path': match.group(1).strip(),
                'line': int(match.group(2)),
                'column': int(match.group(3)),
                'error_code': match.group(4).strip(),
                'message': match.group(5).strip(),
                'timestamp': datetime.now().isoformat(),
                'stack_trace': None
            })

        # Find all runtime exceptions
        exception_matches = list(self.patterns['exception'].finditer(content))
        for i, match in enumerate(exception_matches):
            exception_type = match.group(1).strip()
            exception_message = match.group(2).strip()

            # Try to find stack trace for this exception
            # Look ahead in content for stack trace lines
            exception_end = match.end()
            content_after = content[exception_end:exception_end + 2000]  # Look ahead 2KB

            stack_traces = []
            file_path = None
            line_number = None
            method_name = None

            for stack_match in self.patterns['stack_trace'].finditer(content_after):
                stack_info = {
                    'method': stack_match.group(1).strip(),
                    'file': stack_match.group(2).strip(),
                    'line': int(stack_match.group(3))
                }
                stack_traces.append(stack_info)

                # First stack frame is usually the error location
                if not file_path and 'Assets' in stack_info['file']:
                    file_path = stack_info['file']
                    line_number = stack_info['line']
                    method_name = stack_info['method']

            errors.append({
                'type': exception_type,
                'severity': 'exception',
                'file_path': file_path or 'Unknown',
                'line': line_number or 0,
                'method': method_name or 'Unknown',
                'message': exception_message,
                'timestamp': datetime.now().isoformat(),
                'stack_trace': stack_traces[:10]  # Limit to first 10 frames
            })

        # Find assertions
        for match in self.patterns['assertion'].finditer(content):
            errors.append({
                'type': 'Assertion',
                'severity': 'assertion',
                'message': match.group(1).strip(),
                'timestamp': datetime.now().isoformat()
            })

        return errors

    def get_error_summary(self) -> Dict:
        """
        Get summary of all detected errors.

        Returns:
            Dict with error statistics
        """
        if not self.detected_errors:
            return {
                'total_errors': 0,
                'by_type': {},
                'by_severity': {},
                'recent_errors': []
            }

        # Count by type
        by_type = {}
        by_severity = {}
        for error in self.detected_errors:
            error_type = error.get('type', 'Unknown')
            severity = error.get('severity', 'unknown')

            by_type[error_type] = by_type.get(error_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            'total_errors': len(self.detected_errors),
            'by_type': by_type,
            'by_severity': by_severity,
            'recent_errors': self.detected_errors[-5:]  # Last 5 errors
        }

    def format_error_for_ai(self, error: Dict) -> str:
        """
        Format error in a structured way for AI analysis.

        Args:
            error: Error dictionary from _parse_errors

        Returns:
            Formatted string ready for AI prompt
        """
        lines = [
            "🔍 ERROR DETECTED:",
            f"Type: {error.get('type', 'Unknown')}",
            f"Severity: {error.get('severity', 'unknown')}",
            f"Message: {error.get('message', 'No message')}",
            ""
        ]

        if error.get('file_path') and error['file_path'] != 'Unknown':
            lines.append(f"Location: {error['file_path']}:{error.get('line', 0)}")

        if error.get('method'):
            lines.append(f"Method: {error['method']}")

        if error.get('error_code'):
            lines.append(f"Error Code: {error['error_code']}")

        if error.get('stack_trace'):
            lines.append("")
            lines.append("STACK TRACE:")
            for frame in error['stack_trace'][:5]:  # Top 5 frames
                lines.append(f"  at {frame['method']}")
                lines.append(f"     in {frame['file']}:{frame['line']}")

        lines.append("")
        lines.append(f"Timestamp: {error.get('timestamp', 'Unknown')}")

        return "\n".join(lines)

    def extract_code_context(self, file_path: str, line: int, context_lines: int = 20) -> Optional[str]:
        """
        Extract code around the error line for context.

        Args:
            file_path: Path to source file
            line: Line number of error
            context_lines: Number of lines to show before and after (total = 2*context_lines+1)

        Returns:
            Code context string or None if file not found
        """
        if not file_path or not os.path.exists(file_path):
            return None

        # Check cache first (Phase 3 Performance Optimization)
        cache_key = (file_path, line, context_lines)
        if cache_key in self._code_context_cache:
            return self._code_context_cache[cache_key]

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()

            # Calculate range (1-indexed for display, 0-indexed for array)
            start_line = max(0, line - context_lines - 1)
            end_line = min(len(all_lines), line + context_lines)

            # Extract context
            context_lines_text = []
            for i in range(start_line, end_line):
                line_num = i + 1
                line_text = all_lines[i].rstrip('\n')
                marker = ' >>> ' if line_num == line else '     '
                context_lines_text.append(f"{marker}{line_num:4d} | {line_text}")

            result = "\n".join(context_lines_text)

            # Cache the result
            if len(self._code_context_cache) >= self._cache_max_size:
                # Remove oldest entry (simple FIFO)
                first_key = next(iter(self._code_context_cache))
                del self._code_context_cache[first_key]

            self._code_context_cache[cache_key] = result
            return result

        except Exception as e:
            return f"Error reading file: {str(e)}"

    def clear_errors(self):
        """Clear the detected errors list."""
        self.detected_errors = []


# Example usage and testing
if __name__ == "__main__":
    print("Unity Log Detective - Test Mode")
    print("=" * 60)

    detective = UnityLogDetective()

    if not detective.log_path:
        print("ERROR: Could not find Unity Editor.log")
        print("Please specify path manually:")
        print("  detective = UnityLogDetective('/path/to/Editor.log')")
    else:
        print(f"Monitoring: {detective.log_path}")
        print(f"File exists: {os.path.exists(detective.log_path)}")
        print()
        print("Watching for errors... (Press Ctrl+C to stop)")
        print()

        try:
            while True:
                result = detective.watch_log(check_interval=1.0)

                if result['status'] == 'errors_found':
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {result['count']} new error(s)!")
                    print()

                    for error in result['errors']:
                        print(detective.format_error_for_ai(error))
                        print()

                        # If we have file path and line, show code context
                        if error.get('file_path') and error['file_path'] != 'Unknown':
                            context = detective.extract_code_context(
                                error['file_path'],
                                error.get('line', 0)
                            )
                            if context:
                                print("CODE CONTEXT:")
                                print(context)
                                print()

                    print("-" * 60)

                time.sleep(1.0)

        except KeyboardInterrupt:
            print("\n\nStopped monitoring.")
            summary = detective.get_error_summary()
            print(f"\nSession Summary:")
            print(f"Total errors detected: {summary['total_errors']}")
            if summary['by_type']:
                print("\nBy type:")
                for error_type, count in summary['by_type'].items():
                    print(f"  {error_type}: {count}")
