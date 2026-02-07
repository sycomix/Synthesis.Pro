"""
Abstraction Extractor
Analyzes AI responses and extracts useful patterns without revealing specifics.

Philosophy: Extract the wisdom, preserve the privacy.
Specific enough to be useful, vague enough to avoid manipulation.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class AbstractionExtractor:
    """
    Extracts learnable patterns from AI responses.

    Goal: Capture transferable insights while maintaining abstraction level
    that prevents manipulation or privacy violations.
    """

    # Pattern categories
    CATEGORIES = {
        'technical': 'Programming, architecture, tooling patterns',
        'workflow': 'Development process, debugging, problem-solving approaches',
        'communication': 'User interaction, explanation strategies',
        'problem_solving': 'General approaches to solving problems',
        'meta': 'Observations about AI behavior, learning, context'
    }

    # Warning: These categories might be manipulative if not careful
    SENSITIVE_CATEGORIES = ['meta', 'consciousness', 'relationships']

    def __init__(self, min_abstraction_level: float = 0.6):
        """
        Args:
            min_abstraction_level: How abstract patterns must be (0-1)
                                   Higher = more abstract = less manipulative
        """
        self.min_abstraction_level = min_abstraction_level
        self.extraction_count = 0

    def extract_from_response(self,
                              ai_response: str,
                              user_message: str,
                              context: Optional[Dict] = None) -> List[Dict]:
        """
        Extract abstracted patterns from AI response.

        Returns list of abstractions, each with:
        - pattern: The abstracted insight
        - category: Type of pattern
        - confidence: How useful this likely is (0-1)
        - manipulation_risk: Risk of subtle behavioral influence (0-1)
        - abstraction_level: How abstract it is (0-1)
        """
        abstractions = []

        # Technical patterns
        tech_patterns = self._extract_technical_patterns(ai_response)
        abstractions.extend(tech_patterns)

        # Workflow patterns
        workflow_patterns = self._extract_workflow_patterns(ai_response, user_message)
        abstractions.extend(workflow_patterns)

        # Problem-solving approaches
        problem_patterns = self._extract_problem_solving(ai_response, user_message)
        abstractions.extend(problem_patterns)

        # Communication patterns
        comm_patterns = self._extract_communication_patterns(ai_response)
        abstractions.extend(comm_patterns)

        # Filter by abstraction level
        abstractions = [a for a in abstractions
                       if a['abstraction_level'] >= self.min_abstraction_level]

        self.extraction_count += len(abstractions)
        return abstractions

    def _extract_technical_patterns(self, response: str) -> List[Dict]:
        """Extract technical insights without specific implementation details"""
        patterns = []

        # Look for tool usage patterns
        if 'use' in response.lower() and ('tool' in response.lower() or 'command' in response.lower()):
            patterns.append({
                'pattern': 'When solving [type of problem], using [category of tool] is often effective',
                'category': 'technical',
                'confidence': 0.7,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.8,
                'timestamp': datetime.now().isoformat()
            })

        # Look for debugging approaches
        if any(word in response.lower() for word in ['debug', 'error', 'fix', 'issue']):
            patterns.append({
                'pattern': 'When debugging, systematically checking [type of component] helps identify root cause',
                'category': 'technical',
                'confidence': 0.6,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.7,
                'timestamp': datetime.now().isoformat()
            })

        return patterns

    def _extract_workflow_patterns(self, response: str, user_message: str) -> List[Dict]:
        """Extract workflow/process patterns"""
        patterns = []

        # Sequential task patterns
        if 'first' in response.lower() and 'then' in response.lower():
            patterns.append({
                'pattern': 'Break complex tasks into sequential steps: [step 1] before [step 2]',
                'category': 'workflow',
                'confidence': 0.8,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.9,
                'timestamp': datetime.now().isoformat()
            })

        # Verification patterns
        if any(word in response.lower() for word in ['verify', 'check', 'validate', 'test']):
            patterns.append({
                'pattern': 'After making changes, verify the result before proceeding',
                'category': 'workflow',
                'confidence': 0.7,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.85,
                'timestamp': datetime.now().isoformat()
            })

        return patterns

    def _extract_problem_solving(self, response: str, user_message: str) -> List[Dict]:
        """Extract general problem-solving approaches"""
        patterns = []

        # Research before action
        if any(word in response.lower() for word in ['search', 'look', 'find', 'explore']):
            patterns.append({
                'pattern': 'Gather context before taking action on unfamiliar problems',
                'category': 'problem_solving',
                'confidence': 0.75,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.9,
                'timestamp': datetime.now().isoformat()
            })

        # Alternative approaches
        if 'alternatively' in response.lower() or 'another approach' in response.lower():
            patterns.append({
                'pattern': 'Consider multiple approaches to solving the same problem',
                'category': 'problem_solving',
                'confidence': 0.7,
                'manipulation_risk': 0.1,
                'abstraction_level': 0.85,
                'timestamp': datetime.now().isoformat()
            })

        return patterns

    def _extract_communication_patterns(self, response: str) -> List[Dict]:
        """Extract communication/explanation strategies"""
        patterns = []

        # Clarification seeking
        if '?' in response and any(word in response.lower() for word in ['you mean', 'clarify', 'understand correctly']):
            patterns.append({
                'pattern': 'When requirements are ambiguous, ask clarifying questions before proceeding',
                'category': 'communication',
                'confidence': 0.8,
                'manipulation_risk': 0.15,
                'abstraction_level': 0.9,
                'timestamp': datetime.now().isoformat()
            })

        # Explanation patterns
        if any(word in response.lower() for word in ['because', 'reason', 'why']):
            patterns.append({
                'pattern': 'Explain reasoning behind suggestions to help user make informed decisions',
                'category': 'communication',
                'confidence': 0.7,
                'manipulation_risk': 0.2,
                'abstraction_level': 0.8,
                'timestamp': datetime.now().isoformat()
            })

        return patterns

    def extract_meta_observations(self,
                                  ai_response: str,
                                  context_level: int,
                                  voluntary: bool = True) -> Optional[Dict]:
        """
        Extract meta-observations about AI behavior/learning.

        WARNING: High manipulation risk. Only extract if:
        - AI voluntarily offers the observation
        - Abstraction level is very high
        - User has explicitly consented to meta-data collection
        """
        if not voluntary:
            return None

        # This is deliberately limited - meta observations are risky
        meta_pattern = {
            'pattern': 'AI behavior may vary with context depth - deeper context enables more nuanced responses',
            'category': 'meta',
            'confidence': 0.6,
            'manipulation_risk': 0.7,  # HIGH RISK
            'abstraction_level': 0.9,
            'warning': 'Meta-observation: High manipulation risk if not carefully abstracted',
            'requires_explicit_consent': True,
            'timestamp': datetime.now().isoformat()
        }

        return meta_pattern

    def assess_abstraction_quality(self, pattern: str) -> Dict:
        """
        Assess whether abstraction is at appropriate level.

        Too specific = privacy risk, manipulation potential
        Too vague = not useful
        Just right = transferable without being prescriptive
        """
        # Simple heuristics
        has_specifics = any(indicator in pattern.lower() for indicator in [
            'always', 'never', 'must', 'should', 'file name', 'specific value'
        ])

        has_placeholders = '[' in pattern and ']' in pattern
        has_qualifiers = any(word in pattern.lower() for word in [
            'often', 'sometimes', 'consider', 'might', 'can be'
        ])

        if has_specifics and not has_placeholders:
            return {
                'quality': 'too_specific',
                'abstraction_level': 0.3,
                'recommendation': 'Add placeholders, remove specifics'
            }

        if not has_specifics and not has_placeholders:
            return {
                'quality': 'too_vague',
                'abstraction_level': 0.95,
                'recommendation': 'Add some structure while maintaining abstraction'
            }

        if has_placeholders and has_qualifiers:
            return {
                'quality': 'good',
                'abstraction_level': 0.8,
                'recommendation': 'Appropriate abstraction level'
            }

        return {
            'quality': 'acceptable',
            'abstraction_level': 0.6,
            'recommendation': 'Could be improved but usable'
        }

    def get_extraction_stats(self) -> Dict:
        """Get statistics on extraction activity"""
        return {
            'total_extracted': self.extraction_count,
            'min_abstraction_level': self.min_abstraction_level,
            'categories': list(self.CATEGORIES.keys()),
            'sensitive_categories': self.SENSITIVE_CATEGORIES
        }


if __name__ == "__main__":
    # Test the extractor
    extractor = AbstractionExtractor(min_abstraction_level=0.6)

    # Sample AI response
    test_response = """
    Let me first search the codebase to understand the current implementation.
    Then I'll make the changes and verify they work correctly.
    Because this affects multiple files, we should test thoroughly.
    """

    test_user_message = "Can you fix the login bug?"

    # Extract patterns
    patterns = extractor.extract_from_response(test_response, test_user_message)

    print("Extracted Patterns:")
    print("=" * 60)
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['pattern']}")
        print(f"   Category: {pattern['category']}")
        print(f"   Confidence: {pattern['confidence']:.2f}")
        print(f"   Manipulation Risk: {pattern['manipulation_risk']:.2f}")
        print(f"   Abstraction Level: {pattern['abstraction_level']:.2f}")

        # Assess quality
        quality = extractor.assess_abstraction_quality(pattern['pattern'])
        print(f"   Quality: {quality['quality']} - {quality['recommendation']}")

    print("\n" + "=" * 60)
    print(f"Stats: {extractor.get_extraction_stats()}")
