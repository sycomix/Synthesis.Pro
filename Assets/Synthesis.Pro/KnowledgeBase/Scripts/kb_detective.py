"""
Knowledge Base Detective - Error pattern detection and solution matching
Part of Synthesis AI Detective Mode

Searches the Knowledge Base for similar past errors, detects patterns,
and provides context-aware debugging assistance.

Zero external dependencies - uses only Python standard library.
"""

import sqlite3
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class KnowledgeBaseDetective:
    """
    Searches Knowledge Base for similar errors and detects patterns.
    Links current errors to past solutions for intelligent debugging.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the KB Detective.

        Args:
            db_path: Optional path to knowledge_base.db. If None, auto-detects.
        """
        self.db_path = db_path or self._find_knowledge_base()
        self._ensure_tables()

        # Search result cache (Phase 3 Performance Optimization)
        # Cache key: (error_type, file_name) -> search results
        self._search_cache = {}
        self._cache_max_size = 100
        self._cache_ttl = 300  # Cache time-to-live: 5 minutes

    def _find_knowledge_base(self) -> str:
        """
        Auto-detect knowledge_base.db location.

        Returns:
            Path to knowledge_base.db
        """
        # Look in current directory and parent directories
        current = Path(__file__).parent
        for _ in range(3):  # Search up to 3 levels
            db_path = current / 'knowledge_base.db'
            if db_path.exists():
                return str(db_path)
            current = current.parent

        # Default to same directory as this script
        return str(Path(__file__).parent / 'knowledge_base.db')

    def _ensure_tables(self):
        """Create error_solutions table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create error_solutions table for archiving solved errors
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    error_message TEXT NOT NULL,
                    code_context TEXT,
                    solution TEXT NOT NULL,
                    fix_applied TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    conversation_id INTEGER,
                    times_occurred INTEGER DEFAULT 1,
                    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id)
                )
            """)

            # Create indexes for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_type
                ON error_solutions(error_type)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_path
                ON error_solutions(file_path)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON error_solutions(timestamp DESC)
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Warning: Could not create error_solutions table: {e}")

    def search_similar_errors(self, error: Dict) -> List[Dict]:
        """
        Search Knowledge Base for similar past errors.

        Args:
            error: Error dict from UnityLogDetective

        Returns:
            List of similar error cases with solutions
        """
        if not Path(self.db_path).exists():
            return []

        error_type = error.get('type', 'Unknown')
        file_path = error.get('file_path', '')
        file_name = Path(file_path).name if file_path else ''

        # Check cache first (Phase 3 Performance Optimization)
        cache_key = (error_type, file_name)
        if cache_key in self._search_cache:
            cached_result, timestamp = self._search_cache[cache_key]
            # Check if cache is still valid (within TTL)
            if (time.time() - timestamp) < self._cache_ttl:
                return cached_result

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            method = error.get('method', '')
            message = error.get('message', '')

            similar_errors = []

            # Strategy 1: Search error_solutions table (most precise)
            if file_name:
                cursor.execute("""
                    SELECT error_type, file_path, error_message, solution,
                           fix_applied, timestamp, times_occurred
                    FROM error_solutions
                    WHERE error_type = ?
                      AND (file_path LIKE ? OR file_path LIKE ?)
                    ORDER BY timestamp DESC
                    LIMIT 3
                """, (error_type, f'%{file_name}%', f'%{file_name.replace(".cs", "")}%'))

                for row in cursor.fetchall():
                    similar_errors.append({
                        'source': 'error_solutions',
                        'error_type': row[0],
                        'file_path': row[1],
                        'problem': row[2],
                        'solution': row[3],
                        'fix': row[4],
                        'date': self._format_date(row[5]),
                        'occurrences': row[6],
                        'similarity': 0.95  # High confidence - exact error type + file
                    })

            # Strategy 2: Search ai_conversations for debugging sessions
            search_terms = []
            if error_type:
                search_terms.append(error_type)
            if file_name:
                search_terms.append(file_name.replace('.cs', ''))
            if method:
                search_terms.append(method.split('(')[0])  # Method name without params

            if search_terms:
                # Build LIKE query for flexible matching
                like_clauses = ' AND '.join(['user_message LIKE ?' for _ in search_terms])
                like_params = [f'%{term}%' for term in search_terms]

                cursor.execute(f"""
                    SELECT user_message, ai_response, timestamp
                    FROM ai_conversations
                    WHERE {like_clauses}
                      AND (user_message LIKE '%error%'
                           OR user_message LIKE '%exception%'
                           OR user_message LIKE '%bug%'
                           OR user_message LIKE '%fix%')
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, like_params)

                for row in cursor.fetchall():
                    user_msg = row[0][:200]  # First 200 chars
                    ai_response = row[1][:300] if row[1] else 'No solution recorded'

                    similar_errors.append({
                        'source': 'conversations',
                        'problem': user_msg,
                        'solution': ai_response,
                        'date': self._format_date(row[2]),
                        'similarity': 0.75  # Medium confidence - keyword match
                    })

            # Strategy 3: Search for error type only (broader match)
            if not similar_errors and error_type:
                cursor.execute("""
                    SELECT user_message, ai_response, timestamp
                    FROM ai_conversations
                    WHERE user_message LIKE ?
                      AND (user_message LIKE '%error%' OR user_message LIKE '%exception%')
                    ORDER BY timestamp DESC
                    LIMIT 3
                """, (f'%{error_type}%',))

                for row in cursor.fetchall():
                    similar_errors.append({
                        'source': 'conversations_broad',
                        'problem': row[0][:200],
                        'solution': row[1][:300] if row[1] else 'No solution',
                        'date': self._format_date(row[2]),
                        'similarity': 0.50  # Lower confidence - error type only
                    })

            conn.close()

            # Sort by similarity score and return top results
            similar_errors.sort(key=lambda x: x['similarity'], reverse=True)
            results = similar_errors[:5]  # Top 5 most relevant

            # Cache the results (Phase 3 Performance Optimization)
            if len(self._search_cache) >= self._cache_max_size:
                # Remove oldest entry (simple FIFO)
                first_key = next(iter(self._search_cache))
                del self._search_cache[first_key]

            self._search_cache[cache_key] = (results, time.time())
            return results

        except Exception as e:
            print(f"Error searching KB: {e}")
            return []

    def detect_error_pattern(self, error: Dict, lookback_days: int = 30) -> Optional[Dict]:
        """
        Detect if this error is part of a recurring pattern.

        Args:
            error: Error dict from UnityLogDetective
            lookback_days: How many days to look back for patterns

        Returns:
            Pattern analysis dict or None
        """
        if not Path(self.db_path).exists():
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            error_type = error.get('type', 'Unknown')
            file_path = error.get('file_path', '')
            file_name = Path(file_path).name if file_path else ''

            # Calculate lookback date
            cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()

            # Check error_solutions table for recurring issues
            cursor.execute("""
                SELECT COUNT(*) as occurrences,
                       MAX(timestamp) as last_seen,
                       MIN(timestamp) as first_seen,
                       error_message
                FROM error_solutions
                WHERE error_type = ?
                  AND (file_path LIKE ? OR file_path LIKE ?)
                  AND timestamp > ?
                GROUP BY SUBSTR(error_message, 1, 100)
                HAVING occurrences > 1
                ORDER BY occurrences DESC
                LIMIT 1
            """, (error_type, f'%{file_name}%', f'%{file_name.replace(".cs", "")}%', cutoff_date))

            row = cursor.fetchone()
            if row:
                occurrences = row[0]
                last_seen = row[1]
                first_seen = row[2]
                message = row[3]

                # Calculate trend
                first_dt = datetime.fromisoformat(first_seen)
                last_dt = datetime.fromisoformat(last_seen)
                days_span = (last_dt - first_dt).days or 1
                frequency = occurrences / days_span

                trend = 'increasing' if frequency > 0.5 else 'stable'

                conn.close()

                return {
                    'occurrences': occurrences,
                    'first_seen': self._format_date(first_seen),
                    'last_seen': self._format_date(last_seen),
                    'trend': trend,
                    'frequency': f'{frequency:.1f} times/day',
                    'message_preview': message[:100],
                    'is_recurring': occurrences >= 3,
                    'severity': 'high' if occurrences >= 5 else 'medium'
                }

            # Also check conversations for similar error discussions
            cursor.execute("""
                SELECT COUNT(*) as mentions
                FROM ai_conversations
                WHERE user_message LIKE ?
                  AND user_message LIKE ?
                  AND timestamp > ?
            """, (f'%{error_type}%', f'%{file_name}%', cutoff_date))

            mentions = cursor.fetchone()[0]
            conn.close()

            if mentions >= 2:
                return {
                    'occurrences': mentions,
                    'trend': 'recurring',
                    'source': 'conversations',
                    'is_recurring': True,
                    'severity': 'medium'
                }

            return None

        except Exception as e:
            print(f"Error detecting pattern: {e}")
            return None

    def archive_solution(self, error: Dict, solution: str, fix_code: Optional[str] = None,
                        conversation_id: Optional[int] = None) -> Optional[int]:
        """
        Archive a solved error to the Knowledge Base.

        Args:
            error: Error dict from UnityLogDetective
            solution: AI's explanation of the solution
            fix_code: Optional code that fixed the error
            conversation_id: Optional link to ai_conversations table

        Returns:
            Solution ID if successfully archived, None otherwise
        """
        if not Path(self.db_path).exists():
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if similar error already exists (update instead of insert)
            cursor.execute("""
                SELECT id, times_occurred FROM error_solutions
                WHERE error_type = ?
                  AND file_path = ?
                  AND line_number = ?
                  AND error_message = ?
            """, (
                error.get('type', 'Unknown'),
                error.get('file_path', 'Unknown'),
                error.get('line', 0),
                error.get('message', '')
            ))

            existing = cursor.fetchone()
            solution_id = None

            if existing:
                # Update existing record
                solution_id = existing[0]
                cursor.execute("""
                    UPDATE error_solutions
                    SET solution = ?,
                        fix_applied = ?,
                        timestamp = CURRENT_TIMESTAMP,
                        times_occurred = times_occurred + 1,
                        conversation_id = ?
                    WHERE id = ?
                """, (solution, fix_code, conversation_id, solution_id))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO error_solutions
                    (error_type, file_path, line_number, error_message,
                     code_context, solution, fix_applied, conversation_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    error.get('type', 'Unknown'),
                    error.get('file_path', 'Unknown'),
                    error.get('line', 0),
                    error.get('message', ''),
                    error.get('code_context', ''),
                    solution,
                    fix_code,
                    conversation_id
                ))
                solution_id = cursor.lastrowid

            conn.commit()
            conn.close()
            return solution_id

        except Exception as e:
            print(f"Error archiving solution: {e}")
            return None

    def get_recent_changes(self, file_path: str, days: int = 7) -> List[Dict]:
        """
        Find recent conversations about a specific file.

        Args:
            file_path: Path to source file
            days: How many days to look back

        Returns:
            List of recent conversations about this file
        """
        if not Path(self.db_path).exists():
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            file_name = Path(file_path).name if file_path else ''
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute("""
                SELECT user_message, ai_response, timestamp
                FROM ai_conversations
                WHERE (user_message LIKE ? OR ai_response LIKE ?)
                  AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 5
            """, (f'%{file_name}%', f'%{file_name}%', cutoff_date))

            changes = []
            for row in cursor.fetchall():
                changes.append({
                    'user_query': row[0][:150],
                    'ai_action': row[1][:150] if row[1] else 'No response',
                    'date': self._format_date(row[2])
                })

            conn.close()
            return changes

        except Exception as e:
            print(f"Error getting recent changes: {e}")
            return []

    def _format_date(self, timestamp: str) -> str:
        """
        Format timestamp for display.

        Args:
            timestamp: ISO format timestamp

        Returns:
            Human-readable date string
        """
        try:
            dt = datetime.fromisoformat(timestamp)
            now = datetime.now()
            delta = now - dt

            if delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Yesterday"
            elif delta.days < 7:
                return f"{delta.days} days ago"
            else:
                return dt.strftime("%b %d")
        except:
            return timestamp[:10]  # Fallback to date only

    def export_anonymized_solutions(self, days: int = 90, min_quality: int = 1) -> List[Dict]:
        """
        Export anonymized solutions for community sharing (Phase 4 Privacy).

        PRIVACY: Strips all project-specific data:
        - Removes file paths
        - Removes specific line numbers
        - Generalizes error messages (removes variable names)
        - Keeps generic solution patterns only

        Args:
            days: Look back this many days
            min_quality: Minimum quality rating (future feature)

        Returns:
            List of anonymized solution dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get solutions from error_solutions table
        cursor.execute("""
            SELECT
                error_type,
                error_message,
                solution,
                fix_code,
                tags,
                unity_version,
                timestamp
            FROM error_solutions
            WHERE timestamp > ?
            AND solution IS NOT NULL
            ORDER BY timestamp DESC
        """, (cutoff_date,))

        anonymized = []
        for row in cursor.fetchall():
            error_type, error_msg, solution, fix_code, tags, unity_ver, timestamp = row

            # Anonymize error message (remove specific variable/method names)
            error_pattern = self._anonymize_error_message(error_msg) if error_msg else None

            # Anonymize fix code (keep pattern, remove specifics)
            fix_pattern = self._anonymize_code(fix_code) if fix_code else None

            # Keep solution text (usually generic enough already)
            # But scan for project-specific terms
            solution_text = self._sanitize_solution(solution) if solution else None

            anonymized.append({
                'error_type': error_type,
                'error_pattern': error_pattern,
                'solution': solution_text,
                'fix_pattern': fix_pattern,
                'tags': tags,
                'unity_version': unity_ver,
                'month': timestamp[:7] if timestamp else None,  # YYYY-MM only (not specific date)
                # NOTE: NO file_path, NO line number, NO project name
            })

        conn.close()
        return anonymized

    def _anonymize_error_message(self, message: str) -> str:
        """
        Anonymize error message by removing project-specific names.

        Example:
          "NightBlade.Combat.WeaponController.Attack()" -> "ProjectName.Module.Controller.Method()"
          "playerInventory is null" -> "componentReference is null"
        """
        if not message:
            return message

        # Remove specific class/namespace paths, keep structure
        # Match pattern like: Word.Word.Word.Method()
        message = re.sub(r'\b[A-Z][a-zA-Z0-9_]*(\.[A-Z][a-zA-Z0-9_]*){2,}', 'ClassName.Method', message)

        # Generalize camelCase variable names
        message = re.sub(r'\b[a-z][a-zA-Z0-9_]*(?=\s+(?:is|was|has|cannot|could not|reference|null|missing))', 'variableName', message)

        return message

    def _anonymize_code(self, code: str) -> str:
        """
        Anonymize code by keeping structure but removing specific names.

        Example:
          "weaponInventory = GetComponent<WeaponInventory>()" -> "component = GetComponent<ComponentType>()"
          "attackManager.PerformAttack()" -> "manager.PerformAction()"
        """
        if not code:
            return code

        # Replace specific variable names with generic ones
        code = re.sub(r'\b[a-z][a-zA-Z0-9_]+(?=\s*=)', 'variableName', code)

        # Replace specific type names in generics with generic placeholder
        code = re.sub(r'<([A-Z][a-zA-Z0-9_]+)>', '<ComponentType>', code)

        # Replace method calls with generic pattern
        code = re.sub(r'\.([A-Z][a-zA-Z0-9_]+)\(', '.MethodName(', code)

        return code

    def _sanitize_solution(self, solution: str) -> str:
        """
        Sanitize solution text by removing project-specific references.

        Keeps the debugging logic, removes specific project names.
        """
        if not solution:
            return solution

        # Remove specific project name references (e.g., "NightBlade", "YourProject")
        solution = re.sub(r'\b[A-Z][a-z]+[A-Z][a-zA-Z0-9_]*\b(?=\s+(?:system|manager|controller|handler))', 'Project', solution)

        # Keep the solution otherwise intact - it's usually generic enough
        return solution


# Example usage and testing
if __name__ == "__main__":
    print("Knowledge Base Detective - Test Mode")
    print("=" * 60)

    detective = KnowledgeBaseDetective()
    print(f"Database: {detective.db_path}")
    print(f"Database exists: {Path(detective.db_path).exists()}")
    print()

    # Test with sample error
    test_error = {
        'type': 'NullReferenceException',
        'message': 'Object reference not set to an instance of an object',
        'file_path': 'Assets/Scripts/PlayerController.cs',
        'line': 45,
        'method': 'Start()',
        'severity': 'exception'
    }

    print("Testing similar error search...")
    similar = detective.search_similar_errors(test_error)
    print(f"Found {len(similar)} similar cases:")
    for i, case in enumerate(similar, 1):
        print(f"\n{i}. [{case.get('source')}] Similarity: {case['similarity']:.0%}")
        print(f"   Date: {case['date']}")
        print(f"   Problem: {case['problem'][:100]}...")
        if case.get('solution'):
            print(f"   Solution: {case['solution'][:100]}...")

    print("\n" + "-" * 60)
    print("\nTesting pattern detection...")
    pattern = detective.detect_error_pattern(test_error)
    if pattern:
        print(f"Pattern detected!")
        print(f"  Occurrences: {pattern['occurrences']}")
        print(f"  Trend: {pattern['trend']}")
        print(f"  Recurring: {pattern.get('is_recurring', False)}")
    else:
        print("No pattern detected (first occurrence)")

    print("\n" + "-" * 60)
    print("\nTesting recent changes...")
    changes = detective.get_recent_changes(test_error['file_path'])
    print(f"Found {len(changes)} recent discussions about this file:")
    for i, change in enumerate(changes, 1):
        print(f"\n{i}. {change['date']}")
        print(f"   Query: {change['user_query']}...")

    print("\n" + "-" * 60)
    print("\nTesting solution archiving...")
    success = detective.archive_solution(
        test_error,
        solution="Changed GetComponent<InputSystem>() to InputManager.Instance",
        fix_code="inputSystem = InputManager.Instance;",
        conversation_id=None
    )
    print(f"Archive success: {success}")
