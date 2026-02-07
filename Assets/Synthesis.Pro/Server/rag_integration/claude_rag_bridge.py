"""
Claude Code RAG Bridge
Provides RAG context to Claude Code sessions on startup.

This bridges the RAG onboarding system to Claude Code's environment.
Run this at the start of a Claude Code session to get relevant context.
"""

import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))  # Server/ directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))  # RAG/core/ directory

from rag_engine_lite import SynthesisRAG
from rag_integration.rag_onboarding import RAGOnboardingSystem


def generate_context_for_claude():
    """
    Generate RAG context for Claude Code session.

    Returns formatted context string ready for Claude to consume.
    """
    try:
        # Initialize RAG with dual databases
        server_dir = Path(__file__).parent.parent  # Server/ directory
        db_dir = server_dir / "database"

        rag = SynthesisRAG(
            database=str(db_dir / "synthesis_knowledge.db"),
            private_database=str(db_dir / "synthesis_private.db")
        )

        # Initialize onboarding system
        onboarding = RAGOnboardingSystem(
            rag_engine=rag,
            user_id="claude_code_session",
            presentation_style="natural"
        )

        # Generate session preview
        import uuid
        session_id = f"claude_{uuid.uuid4().hex[:8]}"
        context = onboarding.start_session(session_id)

        if context:
            from datetime import datetime
            return f"""
# Current Session State

**Session started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

{context}

---
*Context auto-retrieved from knowledge base. Continue this work or start fresh - your call.*
"""
        else:
            return None

    except Exception as e:
        return f"# RAG Context Unavailable\n\nError loading context: {str(e)}\n"


def write_to_memory():
    """Write RAG context to Claude Code's auto memory"""
    try:
        # Get context
        context = generate_context_for_claude()

        # Get memory file path
        memory_dir = Path.home() / ".claude" / "projects" / "d--Unity-Projects-Synthesis-Pro" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        memory_file = memory_dir / "MEMORY.md"

        # Read current MEMORY.md
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
        else:
            current_content = "# Synthesis.Pro Memory\n\n"

        # Remove old session context if it exists (both old and new format)
        section_marker = "## Current Session State" if "## Current Session State" in current_content else "## RAG Session Context"
        if section_marker in current_content:
            # Split at the section and remove it
            parts = current_content.split(section_marker)
            base_content = parts[0].rstrip()

            # Check if there's content after the RAG section
            if len(parts) > 1:
                # Find the next ## section
                remaining = parts[1]
                next_section = remaining.find("\n## ")
                if next_section != -1:
                    base_content += "\n\n" + remaining[next_section+1:]
        else:
            base_content = current_content.rstrip()

        # Add fresh RAG context if available
        if context:
            new_content = f"{base_content}\n\n## RAG Session Context\n\n{context.strip()}\n"
            print("[OK] RAG context updated in MEMORY.md")
        else:
            new_content = base_content + "\n"
            print("[OK] No RAG context available - MEMORY.md kept as-is")

        # Write updated memory
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Memory file: {memory_file}")
        if context:
            print("\nRAG Context preview:")
            print("=" * 60)
            # Show just the RAG context part, not the whole MEMORY.md
            preview = context.strip()
            print(preview[:500] + "..." if len(preview) > 500 else preview)
            print("=" * 60)

    except Exception as e:
        print(f"[ERROR] Error writing RAG context: {e}")
        import traceback
        traceback.print_exc()


def output_context():
    """Output RAG context to stdout for manual consumption"""
    context = generate_context_for_claude()

    if context:
        print(context)
    else:
        print("No RAG context available - starting with a clean slate.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate RAG context for Claude Code")
    parser.add_argument('--write', action='store_true',
                       help='Write to memory file instead of stdout')
    parser.add_argument('--output', action='store_true',
                       help='Output to stdout (default)')

    args = parser.parse_args()

    if args.write:
        write_to_memory()
    else:
        output_context()
