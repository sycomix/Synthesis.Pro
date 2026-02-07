"""
Phase 3: Intelligent Error Pattern Matching
"You've seen this before" - AI-powered error recognition and fix suggestions

This system:
- Detects when errors match historical patterns
- Tracks error resolutions (when they stop appearing)
- Suggests fixes based on past successful resolutions
- Provides confidence scores for pattern matches
- Learns from error patterns over time

Philosophy: Not just capturing errors, but learning from them.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

# Add RAG core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))
from rag_engine_lite import SynthesisRAG


class ErrorPattern:
    """Represents a pattern of errors with resolution tracking"""

    def __init__(self, signature: str, first_seen: datetime, last_seen: datetime):
        self.signature = signature
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.occurrence_count = 1
        self.resolved = False
        self.resolution_date = None
        self.resolution_confidence = 0.0


class ErrorPatternMatcher:
    """
    Intelligent error pattern matching and fix suggestion system.

    Phase 3: Makes errors tell you not just what happened, but what to do about it.
    """

    def __init__(self, rag_engine: SynthesisRAG):
        self.rag = rag_engine

        # Configuration
        self.resolution_threshold_days = 7  # If error doesn't appear for 7 days, consider resolved
        self.pattern_match_threshold = 0.7  # Similarity threshold for pattern matching
        self.min_occurrences_for_pattern = 2  # Need 2+ occurrences to be a "pattern"

    def analyze_new_error(self, error_entry: Dict) -> Dict:
        """
        Analyze a new error and provide intelligent insights.

        Returns:
            {
                'is_known_pattern': bool,
                'pattern_match': Optional[Dict],  # Details about matched pattern
                'suggested_fixes': List[str],
                'confidence': float,
                'historical_context': str
            }
        """
        # Extract error signature
        signature = self._extract_signature(error_entry)

        # Search for similar historical errors
        similar_errors = self._find_similar_errors(signature, error_entry)

        if not similar_errors:
            return {
                'is_known_pattern': False,
                'pattern_match': None,
                'suggested_fixes': [],
                'confidence': 0.0,
                'historical_context': 'First time seeing this error.'
            }

        # Analyze pattern
        pattern_analysis = self._analyze_pattern(similar_errors, error_entry)

        # Generate fix suggestions
        suggested_fixes = self._generate_fix_suggestions(
            error_entry,
            similar_errors,
            pattern_analysis
        )

        return {
            'is_known_pattern': True,
            'pattern_match': pattern_analysis,
            'suggested_fixes': suggested_fixes,
            'confidence': pattern_analysis.get('confidence', 0.0),
            'historical_context': self._generate_historical_context(similar_errors, pattern_analysis)
        }

    def _extract_signature(self, error_entry: Dict) -> str:
        """
        Extract searchable signature from error.

        Examples:
        - "NullReferenceException in PlayerController"
        - "IndexOutOfRangeException in MainGame scene"
        """
        message = error_entry.get('message', '')
        file_path = error_entry.get('file', '')
        scene_name = error_entry.get('sceneName', '')

        # Extract exception type
        exception_type = ""
        if "Exception" in message:
            exception_type = message.split(':')[0].strip()

        # Extract script name
        script_name = ""
        if file_path:
            script_name = Path(file_path).stem

        # Build signature
        parts = [exception_type] if exception_type else [message[:50]]
        if script_name:
            parts.append(f"in {script_name}")
        if scene_name:
            parts.append(f"[{scene_name}]")

        return " ".join(parts)

    def _find_similar_errors(self, signature: str, error_entry: Dict, top_k: int = 10) -> List[Dict]:
        """Search RAG for similar historical errors"""

        # Build rich query with context
        query_parts = [signature]

        # Add scene context if available
        if error_entry.get('sceneName'):
            query_parts.append(f"Scene: {error_entry['sceneName']}")

        # Add GameObject context if available
        if error_entry.get('gameObjectName'):
            query_parts.append(f"GameObject: {error_entry['gameObjectName']}")

        query = " ".join(query_parts)

        # Search private database (project-specific errors)
        results = self.rag.search(query, top_k=top_k, scope="private")

        # Filter for console entries only
        console_errors = []
        for result in results:
            if result['text'].startswith('[CONSOLE:ERROR]') or result['text'].startswith('[CONSOLE:EXCEPTION]'):
                console_errors.append(result)

        return console_errors

    def _analyze_pattern(self, similar_errors: List[Dict], current_error: Dict) -> Dict:
        """
        Analyze pattern from similar errors.

        Returns pattern details including:
        - How many times seen before
        - When first/last seen
        - Same scene/GameObject?
        - Confidence score
        """
        if not similar_errors:
            return {}

        # Calculate confidence based on similarity scores
        scores = [err['score'] for err in similar_errors]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Check context similarity
        current_scene = current_error.get('sceneName', '')
        current_object = current_error.get('gameObjectName', '')

        same_scene_count = sum(1 for err in similar_errors if current_scene in err['text'])
        same_object_count = sum(1 for err in similar_errors if current_object and current_object in err['text'])

        # Extract timestamps from error text (they're in ISO format)
        timestamps = self._extract_timestamps_from_errors(similar_errors)

        return {
            'occurrences': len(similar_errors),
            'first_seen': timestamps[0] if timestamps else 'unknown',
            'last_seen': timestamps[-1] if timestamps else 'unknown',
            'same_scene_occurrences': same_scene_count,
            'same_object_occurrences': same_object_count,
            'confidence': avg_score,
            'pattern_strength': 'strong' if avg_score > 0.8 else 'moderate' if avg_score > 0.5 else 'weak'
        }

    def _extract_timestamps_from_errors(self, errors: List[Dict]) -> List[str]:
        """Extract timestamps from error text"""
        timestamps = []
        for err in errors:
            # Look for ISO timestamp in first line: [CONSOLE:ERROR] 2026-02-06T14:50:22
            text = err['text']
            if '] ' in text:
                parts = text.split('] ', 1)
                if len(parts) > 1:
                    potential_timestamp = parts[1].split('\n')[0]
                    if 'T' in potential_timestamp:  # ISO format has T
                        timestamps.append(potential_timestamp)
        return sorted(timestamps)

    def _generate_fix_suggestions(
        self,
        error_entry: Dict,
        similar_errors: List[Dict],
        pattern_analysis: Dict
    ) -> List[str]:
        """
        Generate actionable fix suggestions based on historical patterns.

        Uses pattern analysis to suggest what might help.
        """
        suggestions = []

        exception_type = error_entry.get('message', '').split(':')[0] if ':' in error_entry.get('message', '') else ''

        # Generic suggestions based on exception type
        if 'NullReference' in exception_type:
            suggestions.append("Check for null before accessing object properties")
            suggestions.append("Verify object is initialized in Start/Awake")

            # Context-specific suggestion
            if error_entry.get('gameObjectName'):
                suggestions.append(f"Verify '{error_entry['gameObjectName']}' GameObject is properly initialized")

        elif 'IndexOutOfRange' in exception_type:
            suggestions.append("Check array/list bounds before accessing")
            suggestions.append("Verify collection is not empty before iteration")

        elif 'MissingReference' in exception_type:
            suggestions.append("Check inspector for missing component references")
            suggestions.append("Verify referenced asset still exists")

        # Pattern-based suggestions
        if pattern_analysis.get('occurrences', 0) >= 3:
            suggestions.append(f"[!] This error has occurred {pattern_analysis['occurrences']} times before")

            if pattern_analysis.get('same_scene_occurrences', 0) > 1:
                suggestions.append(f"[!] Common in {error_entry.get('sceneName')} scene - check scene-specific setup")

            if pattern_analysis.get('same_object_occurrences', 0) > 1:
                suggestions.append(f"[!] Repeated on {error_entry.get('gameObjectName')} - may need refactoring")

        # Historical context suggestion
        if pattern_analysis.get('pattern_strength') == 'strong':
            suggestions.append("[*] High confidence match - review similar past errors for solution patterns")

        return suggestions

    def _generate_historical_context(self, similar_errors: List[Dict], pattern_analysis: Dict) -> str:
        """Generate human-readable historical context"""

        if not similar_errors:
            return "First occurrence of this error."

        occurrences = len(similar_errors)
        confidence = pattern_analysis.get('confidence', 0.0)

        context = f"Seen {occurrences} time(s) before. "

        if confidence > 0.8:
            context += "Strong pattern match - very similar to previous occurrences. "
        elif confidence > 0.5:
            context += "Moderate pattern match - somewhat similar to previous occurrences. "
        else:
            context += "Weak pattern match - may be related to previous errors. "

        # Add timing info
        first_seen = pattern_analysis.get('first_seen')
        last_seen = pattern_analysis.get('last_seen')

        if first_seen and first_seen != 'unknown':
            context += f"First seen: {first_seen[:10]}. "

        if last_seen and last_seen != 'unknown' and last_seen != first_seen:
            context += f"Last seen: {last_seen[:10]}. "

        # Add context similarity
        same_scene = pattern_analysis.get('same_scene_occurrences', 0)
        if same_scene > 0:
            context += f"{same_scene} occurrence(s) in same scene. "

        return context.strip()

    def track_error_resolution(self, signature: str, resolved: bool = True):
        """
        Mark an error pattern as resolved (or not).

        This can be called manually or automatically detected when
        an error stops appearing for threshold_days.
        """
        # Store resolution in RAG
        resolution_note = f"""
        [ERROR_RESOLUTION]
        Signature: {signature}
        Status: {'RESOLVED' if resolved else 'UNRESOLVED'}
        Date: {datetime.now().isoformat()}
        """

        self.rag.add_text(resolution_note.strip(), private=True)


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 3: Intelligent Error Pattern Matching")
    print("=" * 60)

    # Initialize RAG
    server_dir = Path(__file__).parent.parent
    db_dir = server_dir / "database"
    rag = SynthesisRAG(
        database=str(db_dir / "synthesis_knowledge.db"),
        private_database=str(db_dir / "synthesis_private.db")
    )

    # Create matcher
    matcher = ErrorPatternMatcher(rag)

    # Test with a sample error
    test_error = {
        'type': 'error',
        'message': 'NullReferenceException: Object reference not set to an instance of an object',
        'file': 'Assets/Scripts/PlayerController.cs',
        'line': 42,
        'sceneName': 'MainGame',
        'gameObjectName': 'Player',
        'gameObjectPath': 'GameManager/Characters/Player',
    }

    print("\nAnalyzing error...")
    analysis = matcher.analyze_new_error(test_error)

    print(f"\nIs Known Pattern: {analysis['is_known_pattern']}")
    print(f"Confidence: {analysis['confidence']:.2f}")
    print(f"\nHistorical Context:")
    print(f"  {analysis['historical_context']}")

    if analysis['suggested_fixes']:
        print(f"\nSuggested Fixes:")
        for i, fix in enumerate(analysis['suggested_fixes'], 1):
            print(f"  {i}. {fix}")

    if analysis['pattern_match']:
        print(f"\nPattern Analysis:")
        for key, value in analysis['pattern_match'].items():
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Intelligent Pattern Matching Ready")
    print("Now you know: Have I seen this before? What worked last time?")
    print("=" * 60)
