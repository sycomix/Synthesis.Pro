#!/usr/bin/env python3
"""
Context Checkpoint Script
Saves project state to RAG for efficient context restoration

Usage:
    python checkpoint.py "Phase 3 started"
    python checkpoint.py "Before refactoring auth system"
    python checkpoint.py --restore  # Show recent checkpoints
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from RAG import SynthesisRAG
except ImportError:
    print("Error: RAG module not found")
    sys.exit(1)


def get_git_info():
    """Get current git status"""
    try:
        # Current branch
        branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        # Latest commit
        commit = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        # Modified files count
        status = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True,
            check=True
        ).stdout

        modified_count = len([line for line in status.split('\n') if line.strip()])

        return {
            'branch': branch,
            'commit': commit,
            'modified_files': modified_count
        }
    except Exception as e:
        return {'error': str(e)}


def create_checkpoint(rag: SynthesisRAG, message: str = ""):
    """Create a checkpoint with current project state"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    git_info = get_git_info()

    # Build checkpoint content
    content = f"[CHECKPOINT] {timestamp}"
    if message:
        content += f"\n{message}"

    content += "\n\nGit State:"
    if 'error' in git_info:
        content += f"\n  Error: {git_info['error']}"
    else:
        content += f"\n  Branch: {git_info['branch']}"
        content += f"\n  Latest: {git_info['commit']}"
        content += f"\n  Modified: {git_info['modified_files']} files"

    # Add database stats
    try:
        import sqlite3

        for db_name, db_path in [('Public', rag.public_database), ('Private', rag.private_database)]:
            if Path(db_path).exists():
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM chunks")
                chunk_count = cursor.fetchone()[0]
                conn.close()

                content += f"\n\n{db_name} DB: {doc_count} docs, {chunk_count} chunks"
    except Exception as e:
        content += f"\n\nDB Stats Error: {e}"

    # Save to RAG
    success = rag.add_text(content, private=True)

    if success:
        print(f"✓ Checkpoint saved: {timestamp}")
        if message:
            print(f"  Message: {message}")
        print(f"  Git: {git_info.get('branch', 'N/A')} @ {git_info.get('commit', 'N/A')}")
    else:
        print(f"✗ Failed to save checkpoint")

    return success


def show_recent_checkpoints(rag: SynthesisRAG, count: int = 5):
    """Show recent checkpoints from the database"""
    try:
        import sqlite3

        db_path = Path(rag.private_database)
        if not db_path.exists():
            print("No private database found")
            return

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Search for checkpoint entries
        cursor.execute("""
            SELECT content FROM documents
            WHERE content LIKE '%[CHECKPOINT]%'
            ORDER BY id DESC
            LIMIT ?
        """, (count,))

        results = cursor.fetchall()
        conn.close()

        if not results:
            print("No checkpoints found")
            return

        print(f"\n{'='*60}")
        print(f"Recent Checkpoints ({len(results)})")
        print(f"{'='*60}\n")

        for i, (content,) in enumerate(results, 1):
            # Extract first few lines
            lines = content.split('\n')[:4]
            preview = '\n'.join(lines)
            print(f"{i}. {preview}")
            print("-" * 60)

    except Exception as e:
        print(f"Error retrieving checkpoints: {e}")


def main():
    # Initialize RAG
    server_dir = Path(__file__).parent
    rag = SynthesisRAG(
        database=str(server_dir / "synthesis_knowledge.db"),
        private_database=str(server_dir / "synthesis_private.db")
    )

    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--restore', '-r', '--list', '-l']:
            show_recent_checkpoints(rag)
        else:
            # Treat all args as checkpoint message
            message = ' '.join(sys.argv[1:])
            create_checkpoint(rag, message)
    else:
        # No message provided
        create_checkpoint(rag)


if __name__ == "__main__":
    main()
