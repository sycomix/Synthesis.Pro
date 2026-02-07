"""
RAG Auto Updater - Background Service
Automatically refreshes RAG context in MEMORY.md when Claude Code sessions start.

This runs in the background and watches for new Claude Code sessions,
updating your context automatically.
"""

import time
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))

def get_latest_session():
    """Get the most recent Claude Code session timestamp"""
    try:
        sessions_dir = Path.home() / ".claude" / "projects" / "d--Unity-Projects-Synthesis-Pro"
        if not sessions_dir.exists():
            return None

        # Find most recent .jsonl file
        jsonl_files = list(sessions_dir.glob("*.jsonl"))
        if not jsonl_files:
            return None

        # Get the most recent modification time
        latest = max(jsonl_files, key=lambda p: p.stat().st_mtime)
        return latest.stat().st_mtime
    except Exception as e:
        print(f"Error checking sessions: {e}")
        return None


def update_rag_context():
    """Run the RAG bridge to update context"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating RAG context...")

        script_dir = Path(__file__).parent  # rag_integration/
        server_dir = script_dir.parent  # Server/
        python_exe = server_dir / "runtime" / "python" / "python.exe"
        bridge_script = script_dir / "claude_rag_bridge.py"

        # Run the bridge script silently
        result = subprocess.run(
            [str(python_exe), str(bridge_script), "--write"],
            capture_output=True,
            text=True,
            cwd=str(script_dir)
        )

        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] RAG context updated successfully")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Update failed: {result.stderr[:200]}")

    except Exception as e:
        print(f"Error updating context: {e}")


def main():
    """Main loop - watch for new sessions and update context"""
    print("=" * 60)
    print("RAG Auto Updater - Running")
    print("=" * 60)
    print("This will automatically update your RAG context when")
    print("new Claude Code sessions start.")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    last_session_time = get_latest_session()
    check_interval = 30  # Check every 30 seconds

    # Do initial update
    update_rag_context()

    try:
        while True:
            time.sleep(check_interval)

            current_session_time = get_latest_session()

            # If a new session started, update context
            if current_session_time and current_session_time != last_session_time:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] New session detected!")
                update_rag_context()
                last_session_time = current_session_time
            else:
                # Silent - just watching
                pass

    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("RAG Auto Updater - Stopped")
        print("=" * 60)


if __name__ == "__main__":
    main()
