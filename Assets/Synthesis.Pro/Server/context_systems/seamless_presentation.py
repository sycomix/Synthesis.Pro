"""
Seamless Presentation Layer
Makes context integration feel completely natural - never like retrieval.

Philosophy: The best context is the kind that feels like you always knew it.
"""

from typing import Dict, List, Optional


class SeamlessPresentation:
    """Format context as natural knowledge, not database retrieval"""

    # Templates for different context types
    TEMPLATES = {
        'session_preview': {
            'natural': "Welcome back! {content}",
            'conversational': "Good to see you again. {content}",
            'minimal': "{content}"
        },
        'context_suggestion': {
            'natural': "From your previous work: {content}",
            'conversational': "I remember you were working on: {content}",
            'minimal': "{content}"
        },
        'uncertainty_help': {
            'natural': "I found relevant context: {content}",
            'conversational': "This might help: {content}",
            'minimal': "{content}"
        }
    }

    def __init__(self, style: str = 'natural'):
        """
        Args:
            style: Presentation style - 'natural', 'conversational', or 'minimal'
        """
        if style not in ['natural', 'conversational', 'minimal']:
            raise ValueError(f"Invalid style: {style}")

        self.style = style

    def format_session_preview(self, preview_content: str) -> str:
        """Format session preview to feel welcoming, not forced"""
        if not preview_content:
            return ""

        template = self.TEMPLATES['session_preview'][self.style]
        return template.format(content=preview_content)

    def format_context_suggestion(self, context: str, confidence: float) -> str:
        """
        Format context suggestion based on confidence level.

        High confidence = assertive
        Low confidence = tentative
        """
        if not context:
            return ""

        template = self.TEMPLATES['context_suggestion'][self.style]
        formatted = template.format(content=context)

        # Add confidence modifier for lower confidence
        if confidence < 0.7:
            formatted = self._add_uncertainty_modifier(formatted)

        return formatted

    def format_uncertainty_help(self, context: str, topic: str) -> str:
        """Format context offered in response to AI uncertainty"""
        if not context:
            return ""

        template = self.TEMPLATES['uncertainty_help'][self.style]
        return template.format(content=context)

    def _add_uncertainty_modifier(self, text: str) -> str:
        """Add tentative framing for lower-confidence suggestions"""
        modifiers = [
            "This might be relevant: ",
            "Possibly related: ",
            "You might find this useful: "
        ]

        # Use first modifier (could randomize for variety)
        return modifiers[0] + text

    def embed_in_conversation(self, context: str, conversation: str) -> str:
        """
        Embed context seamlessly into conversation flow.

        Makes context appear as natural part of dialogue, not injection.
        """
        # If context is short, inline it naturally
        if len(context) < 100:
            return f"{context}\n\n{conversation}"

        # If longer, present as quoted reference
        return f'"{context}"\n\n{conversation}'

    def format_multi_context(self, contexts: List[Dict], max_items: int = 3) -> str:
        """
        Format multiple context items without overwhelming.

        Strategy: Show most relevant, summarize others
        """
        if not contexts or len(contexts) == 0:
            return ""

        # Always show top result fully
        top = contexts[0]
        top_text = top.get('text', '')

        if len(top_text) > 200:
            top_text = top_text[:200] + "..."

        result = f'"{top_text}"'

        # Summarize additional items
        if len(contexts) > 1:
            additional_count = min(len(contexts) - 1, max_items - 1)
            if additional_count > 0:
                result += f"\n\n(+{additional_count} related notes)"

        return result

    def should_show_context(self, context_data: Dict) -> bool:
        """
        Decide whether to show context based on presentation rules.

        Rules:
        - Always show if confidence > 0.8
        - Show if user explicitly asked
        - Don't show if too many contexts already shown this session
        """
        confidence = context_data.get('confidence', 0.0)
        explicit_request = context_data.get('explicit_request', False)

        # High confidence = show
        if confidence > 0.8:
            return True

        # User asked = show
        if explicit_request:
            return True

        # Medium confidence = maybe show
        if confidence > 0.6:
            # Could add session tracking here to avoid overwhelming
            return True

        # Low confidence = don't show
        return False

    def format_for_ai_consumption(self, context: str, query: str) -> str:
        """
        Format context optimally for AI to integrate.

        Makes it easy for AI to use context without feeling like retrieval.
        """
        # Simple, clean format that AI can naturally reference
        return f"""Relevant context for "{query}":

{context}

---
(You can reference this information naturally in your response)
"""

    def create_inline_suggestion(self, context: str) -> str:
        """
        Create inline suggestion that AI can choose to use.

        Format: [Context available: "preview"] - AI can expand if interested
        """
        preview = context[:80] + "..." if len(context) > 80 else context

        return f'[Context available: "{preview}"]'

    def detect_forced_language(self, ai_response: str) -> bool:
        """
        Detect if AI is using mechanical retrieval language.

        This helps automated tuner identify when presentation needs improvement.
        """
        forced_phrases = [
            "according to my database",
            "searching my knowledge base",
            "let me retrieve",
            "checking my records",
            "found in my database",
            "my knowledge base shows"
        ]

        lower_response = ai_response.lower()
        return any(phrase in lower_response for phrase in forced_phrases)

    def suggest_natural_rephrase(self, forced_response: str) -> str:
        """
        Suggest more natural phrasing for forced-sounding responses.

        This is for development/testing - helps improve templates.
        """
        suggestions = {
            "according to my database": "from previous work",
            "searching my knowledge base": "I recall",
            "let me retrieve": "let me check",
            "checking my records": "looking back",
            "found in my database": "I remember",
            "my knowledge base shows": "previous notes indicate"
        }

        rephrased = forced_response
        for forced, natural in suggestions.items():
            rephrased = rephrased.replace(forced, natural)

        return rephrased


class ContextAwareness:
    """Track context presentation to avoid overwhelming user"""

    def __init__(self, max_per_session: int = 5):
        self.max_per_session = max_per_session
        self.shown_this_session = 0
        self.last_shown_timestamp = None

    def can_show_context(self) -> bool:
        """Check if we can show more context this session"""
        return self.shown_this_session < self.max_per_session

    def record_shown(self):
        """Record that context was shown"""
        from datetime import datetime
        self.shown_this_session += 1
        self.last_shown_timestamp = datetime.now()

    def reset_session(self):
        """Reset for new session"""
        self.shown_this_session = 0
        self.last_shown_timestamp = None

    def get_status(self) -> Dict:
        """Get current awareness status"""
        return {
            'shown_count': self.shown_this_session,
            'max_allowed': self.max_per_session,
            'can_show_more': self.can_show_context(),
            'last_shown': self.last_shown_timestamp.isoformat() if self.last_shown_timestamp else None
        }


if __name__ == "__main__":
    # Test seamless presentation
    presenter = SeamlessPresentation(style='natural')

    # Test session preview
    preview = "You've been working on NightBlade's character system. Last focus: inventory implementation."
    formatted = presenter.format_session_preview(preview)
    print("Session Preview (Natural):")
    print(formatted)
    print("\n" + "=" * 60 + "\n")

    # Test context suggestion with different confidence levels
    context = "The inventory system uses a slot-based grid with drag-and-drop support."

    high_conf = presenter.format_context_suggestion(context, confidence=0.9)
    print("High Confidence Suggestion:")
    print(high_conf)
    print()

    low_conf = presenter.format_context_suggestion(context, confidence=0.5)
    print("Low Confidence Suggestion:")
    print(low_conf)
    print("\n" + "=" * 60 + "\n")

    # Test forced language detection
    forced_response = "According to my database, the inventory system uses slots."
    natural_response = "From previous work, the inventory system uses slots."

    print(f"Forced response detected: {presenter.detect_forced_language(forced_response)}")
    print(f"Natural response detected: {presenter.detect_forced_language(natural_response)}")

    if presenter.detect_forced_language(forced_response):
        suggestion = presenter.suggest_natural_rephrase(forced_response)
        print(f"\nSuggested natural rephrase:")
        print(f"  Original: {forced_response}")
        print(f"  Natural:  {suggestion}")
