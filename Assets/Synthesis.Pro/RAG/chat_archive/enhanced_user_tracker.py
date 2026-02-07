"""
Enhanced User Tracker - Comprehensive User Study System
Captures everything reasonably possible to learn user preferences and patterns
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class EnhancedUserTracker:
    """
    Comprehensive user behavior and preference tracker.

    Captures:
    - Coding style preferences (naming, formatting, patterns)
    - Interaction patterns (communication style, detail level)
    - Tool usage preferences (which tools, when)
    - Problem-solving approaches
    - Feedback signals (positive/negative responses)
    - Time patterns (when active, session duration)
    - Error patterns (common mistakes, repeated questions)
    - Decision patterns (architectural preferences)
    """

    def __init__(self, rag_engine, conversation_tracker):
        self.rag = rag_engine
        self.tracker = conversation_tracker
        self.session_start = datetime.now()

    # ========== CODING STYLE TRACKING ==========

    def track_coding_style(
        self,
        style_type: str,
        preference: str,
        evidence: str,
        confidence: str = "observed"
    ) -> bool:
        """
        Track user's coding style preferences

        Args:
            style_type: "naming", "formatting", "comments", "patterns", etc.
            preference: The specific preference observed
            evidence: Example or context showing this preference
            confidence: "observed" | "stated" | "inferred"

        Example:
            track_coding_style(
                "naming",
                "PascalCase for classes, camelCase for methods",
                "User wrote: 'class VFXManager' and 'void createEffect()'",
                "observed"
            )
        """
        learning = {
            "category": "coding-style",
            "type": style_type,
            "preference": preference,
            "evidence": evidence,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

        text = (
            f"[CODING_STYLE:{style_type}] {preference}\n"
            f"Evidence: {evidence}\n"
            f"Confidence: {confidence}"
        )

        self.tracker.add_learning(text, "coding-style")
        return True

    def track_pattern_preference(
        self,
        pattern_name: str,
        pattern_type: str,
        context: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Track preferred design patterns and architectural choices

        Args:
            pattern_name: Name of pattern (e.g., "Singleton", "ECS", "Observer")
            pattern_type: "design-pattern" | "architecture" | "algorithm"
            context: Where/when they use it
            reason: Why they prefer it (if stated)

        Example:
            track_pattern_preference(
                "Object Pooling",
                "design-pattern",
                "Used for VFX particles to reduce GC",
                "Performance-critical systems"
            )
        """
        text = f"[PATTERN:{pattern_type}] {pattern_name}\nContext: {context}"
        if reason:
            text += f"\nReason: {reason}"

        return self.tracker.add_learning(text, "design-pattern")

    # ========== INTERACTION STYLE TRACKING ==========

    def track_communication_style(
        self,
        style_aspect: str,
        observation: str,
        examples: List[str] = None
    ) -> bool:
        """
        Track how user prefers to communicate

        Args:
            style_aspect: "verbosity" | "technicality" | "tone" | "directness"
            observation: What you observed
            examples: Example phrases they use

        Example:
            track_communication_style(
                "directness",
                "User prefers direct commands without pleasantries",
                ["just do it", "make it work", "fix this now"]
            )
        """
        text = f"[COMMUNICATION:{style_aspect}] {observation}"
        if examples:
            text += f"\nExamples: {', '.join(examples)}"

        return self.tracker.add_learning(text, "communication-style")

    def track_feedback_signal(
        self,
        signal_type: str,
        user_response: str,
        context: str
    ) -> bool:
        """
        Track user feedback signals to learn what they like/dislike

        Args:
            signal_type: "positive" | "negative" | "correction" | "appreciation"
            user_response: What they said
            context: What prompted this response

        Example:
            track_feedback_signal(
                "positive",
                "perfect! exactly what i needed",
                "Provided concise solution with code example"
            )

            track_feedback_signal(
                "negative",
                "no that's wrong, i wanted X not Y",
                "Misunderstood requirement about VFX system"
            )
        """
        text = (
            f"[FEEDBACK:{signal_type}] \"{user_response}\"\n"
            f"Context: {context}"
        )

        return self.tracker.add_learning(text, "feedback")

    # ========== TOOL USAGE TRACKING ==========

    def track_tool_preference(
        self,
        tool_name: str,
        usage_context: str,
        alternative_rejected: Optional[str] = None
    ) -> bool:
        """
        Track which tools/methods user prefers

        Args:
            tool_name: Tool or method preferred
            usage_context: When/why they use it
            alternative_rejected: What they didn't use

        Example:
            track_tool_preference(
                "MCP ManageVFX",
                "Creating VFX assets programmatically",
                "Manual Unity editor creation"
            )
        """
        text = f"[TOOL_PREFERENCE] {tool_name}\nContext: {usage_context}"
        if alternative_rejected:
            text += f"\nRejected alternative: {alternative_rejected}"

        return self.tracker.add_learning(text, "tool-usage")

    def track_workflow_preference(
        self,
        workflow_description: str,
        frequency: str = "observed-once"
    ) -> bool:
        """
        Track user's preferred workflows

        Args:
            workflow_description: How they like to work
            frequency: "always" | "often" | "sometimes" | "observed-once"

        Example:
            track_workflow_preference(
                "User reads dev log first, then searches KB, then reads files",
                "always"
            )
        """
        text = f"[WORKFLOW] {workflow_description}\nFrequency: {frequency}"
        return self.tracker.add_learning(text, "workflow")

    # ========== PROBLEM-SOLVING PATTERNS ==========

    def track_problem_solving_approach(
        self,
        problem_type: str,
        approach: str,
        outcome: str
    ) -> bool:
        """
        Track how user approaches different types of problems

        Args:
            problem_type: Type of problem
            approach: How they tackled it
            outcome: "successful" | "needed-help" | "abandoned"

        Example:
            track_problem_solving_approach(
                "Performance issue with VFX particles",
                "User profiled first, then tried object pooling",
                "successful"
            )
        """
        text = (
            f"[PROBLEM_SOLVING] {problem_type}\n"
            f"Approach: {approach}\n"
            f"Outcome: {outcome}"
        )

        return self.tracker.add_learning(text, "problem-solving")

    def track_question_pattern(
        self,
        question_type: str,
        question: str,
        frequency: int = 1
    ) -> bool:
        """
        Track types of questions user asks

        Args:
            question_type: "how-to" | "why" | "what-is" | "debug" | "best-practice"
            question: The question asked
            frequency: How many times similar question asked

        Example:
            track_question_pattern(
                "how-to",
                "How do I create VFX assets programmatically?",
                1
            )
        """
        text = f"[QUESTION:{question_type}] \"{question}\"\nFrequency: {frequency}x"
        return self.tracker.add_learning(text, "question-pattern")

    # ========== ERROR PATTERNS ==========

    def track_error_pattern(
        self,
        error_type: str,
        error_description: str,
        resolution: Optional[str] = None,
        preventable: bool = False
    ) -> bool:
        """
        Track recurring errors or mistakes

        Args:
            error_type: Category of error
            error_description: What went wrong
            resolution: How it was fixed
            preventable: Could this be caught earlier?

        Example:
            track_error_pattern(
                "API misuse",
                "Used internal Unity API via reflection",
                "Switch to public API when available",
                True
            )
        """
        text = (
            f"[ERROR_PATTERN:{error_type}] {error_description}\n"
            f"Preventable: {preventable}"
        )
        if resolution:
            text += f"\nResolution: {resolution}"

        return self.tracker.add_learning(text, "error-pattern")

    # ========== TIME & SESSION PATTERNS ==========

    def track_session_metrics(
        self,
        productive_time: int,
        breaks_taken: int,
        tools_used: List[str],
        files_touched: int
    ) -> bool:
        """
        Track session productivity metrics

        Args:
            productive_time: Minutes of active work
            breaks_taken: Number of breaks
            tools_used: List of tools/commands used
            files_touched: Number of files modified

        Example:
            track_session_metrics(
                productive_time=45,
                breaks_taken=1,
                tools_used=["RAG search", "Edit", "Bash"],
                files_touched=7
            )
        """
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60

        text = (
            f"[SESSION_METRICS]\n"
            f"Total duration: {session_duration:.1f} minutes\n"
            f"Productive time: {productive_time} minutes\n"
            f"Breaks: {breaks_taken}\n"
            f"Tools used: {', '.join(tools_used)}\n"
            f"Files touched: {files_touched}"
        )

        return self.tracker.add_learning(text, "session-metrics")

    def track_time_of_day_pattern(
        self,
        activity_type: str,
        performance: str = "normal"
    ) -> bool:
        """
        Track when user works and how productive they are

        Args:
            activity_type: What they're doing
            performance: "high" | "normal" | "low"

        Example:
            track_time_of_day_pattern("deep focus coding", "high")
        """
        hour = datetime.now().hour
        time_category = (
            "early-morning" if hour < 9 else
            "morning" if hour < 12 else
            "afternoon" if hour < 17 else
            "evening" if hour < 21 else
            "late-night"
        )

        text = (
            f"[TIME_PATTERN] {time_category} ({hour:02d}:00)\n"
            f"Activity: {activity_type}\n"
            f"Performance: {performance}"
        )

        return self.tracker.add_learning(text, "time-pattern")

    # ========== DOMAIN EXPERTISE TRACKING ==========

    def track_expertise_level(
        self,
        domain: str,
        level: str,
        evidence: str
    ) -> bool:
        """
        Track user's expertise in different domains

        Args:
            domain: "Unity", "C#", "VFX", "ECS", "networking", etc.
            level: "beginner" | "intermediate" | "expert"
            evidence: What shows this level

        Example:
            track_expertise_level(
                "VFX Graph",
                "intermediate",
                "Understands particle systems but needs help with internal APIs"
            )
        """
        text = (
            f"[EXPERTISE:{domain}] Level: {level}\n"
            f"Evidence: {evidence}"
        )

        return self.tracker.add_learning(text, "expertise")

    def track_knowledge_gap(
        self,
        topic: str,
        gap_description: str,
        filled: bool = False
    ) -> bool:
        """
        Track what user doesn't know yet

        Args:
            topic: Subject area
            gap_description: What they don't know
            filled: Was this gap filled during session?

        Example:
            track_knowledge_gap(
                "Unity VFX Graph",
                "No public API for programmatic asset creation",
                filled=True
            )
        """
        text = (
            f"[KNOWLEDGE_GAP:{topic}] {gap_description}\n"
            f"Filled: {filled}"
        )

        return self.tracker.add_learning(text, "knowledge-gap")

    # ========== PERSONAL PREFERENCES ==========

    def track_personal_preference(
        self,
        preference_type: str,
        preference: str,
        strength: str = "moderate"
    ) -> bool:
        """
        Track personal preferences not related to code

        Args:
            preference_type: "response-style" | "emoji-usage" | "humor" | "formality"
            preference: The preference
            strength: "strong" | "moderate" | "weak"

        Example:
            track_personal_preference(
                "emoji-usage",
                "User uses minimal emojis, prefers plain text",
                "strong"
            )
        """
        text = (
            f"[PERSONAL_PREF:{preference_type}] {preference}\n"
            f"Strength: {strength}"
        )

        return self.tracker.add_learning(text, "personal-preference")

    # ========== CONTEXT ANALYSIS ==========

    def analyze_user_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze a user message to extract insights

        Args:
            message: User's message

        Returns:
            Dictionary of insights
        """
        insights = {
            "length": len(message),
            "has_code": "```" in message or "  " in message,
            "has_question": "?" in message,
            "tone": self._analyze_tone(message),
            "urgency": self._analyze_urgency(message),
            "clarity": self._analyze_clarity(message)
        }

        return insights

    def _analyze_tone(self, message: str) -> str:
        """Analyze message tone"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["please", "thanks", "appreciate"]):
            return "polite"
        elif any(word in message_lower for word in ["!!", "asap", "now", "urgent"]):
            return "urgent"
        elif any(word in message_lower for word in ["lol", "haha", "😄"]):
            return "casual"
        else:
            return "neutral"

    def _analyze_urgency(self, message: str) -> str:
        """Analyze urgency level"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["urgent", "critical", "asap", "now"]):
            return "high"
        elif any(word in message_lower for word in ["soon", "quick", "fast"]):
            return "medium"
        else:
            return "normal"

    def _analyze_clarity(self, message: str) -> str:
        """Analyze how clear the message is"""
        # Simple heuristics
        if len(message) < 10:
            return "unclear-too-short"
        elif "?" in message and len(message.split()) > 50:
            return "clear-detailed"
        elif "?" in message:
            return "clear-concise"
        else:
            return "statement"

    # ========== COMPREHENSIVE SESSION SUMMARY ==========

    def generate_user_profile_summary(self) -> str:
        """
        Generate a comprehensive summary of what we know about the user

        Returns:
            Formatted summary of user profile
        """
        # Search for all learnings about this user
        all_learnings = []

        categories = [
            "coding-style", "design-pattern", "communication-style", "feedback",
            "tool-usage", "workflow", "problem-solving", "question-pattern",
            "error-pattern", "session-metrics", "time-pattern", "expertise",
            "knowledge-gap", "personal-preference"
        ]

        summary_parts = ["# User Profile Summary\n"]

        for category in categories:
            results = self.rag.search(f"[{category.upper()}]", top_k=10, scope="private")
            if results:
                summary_parts.append(f"\n## {category.replace('-', ' ').title()}")
                for r in results[:5]:  # Top 5 per category
                    summary_parts.append(f"- {r['text'][:200]}...")

        return "\n".join(summary_parts)


# Convenience functions for common tracking scenarios

def quick_track_style(rag, tracker, style_dict: Dict[str, str]):
    """
    Quickly track multiple coding style preferences

    Example:
        quick_track_style(rag, tracker, {
            "naming": "PascalCase for classes",
            "formatting": "4-space indentation",
            "comments": "Minimal inline, detailed header comments"
        })
    """
    enhanced = EnhancedUserTracker(rag, tracker)

    for style_type, preference in style_dict.items():
        enhanced.track_coding_style(style_type, preference, "Observed in code", "observed")


def quick_track_feedback(rag, tracker, feedback: str, context: str):
    """
    Quickly track user feedback

    Example:
        quick_track_feedback(rag, tracker,
            "perfect! exactly what i needed",
            "Provided RAG-first workflow solution"
        )
    """
    enhanced = EnhancedUserTracker(rag, tracker)

    signal_type = "positive" if any(word in feedback.lower() for word in
                                    ["good", "perfect", "excellent", "great", "love"])                   else "negative" if any(word in feedback.lower() for word in
                                     ["wrong", "no", "not what", "bad"])                   else "neutral"

    enhanced.track_feedback_signal(signal_type, feedback, context)


if __name__ == "__main__":
    print("Enhanced User Tracker - Comprehensive user study system")
    print("Captures: coding style, communication patterns, tool usage,")
    print("          problem-solving approaches, time patterns, expertise levels,")
    print("          feedback signals, personal preferences, and more!")
