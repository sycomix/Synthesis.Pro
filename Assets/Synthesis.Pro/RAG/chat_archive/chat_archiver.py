"""
Chat Archive & Session Memory System
Dumps IDE conversations to private DB and links to developer log

ENHANCED: Automatically extracts user insights during archiving
- Coding style preferences
- Communication patterns
- Feedback signals
- Tool usage preferences
- Problem-solving approaches
"""
import sqlite3
import json
import uuid
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

class ChatArchiver:
    """Archives IDE chat sessions to private knowledge base"""

    def __init__(self, private_db_path: str = "Server/synthesis_private.db"):
        self.db_path = Path(private_db_path)
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.datetime.now()
        self.messages: List[Dict[str, Any]] = []
        self.files_modified: List[str] = []
        self.decisions_made: List[str] = []
        self.learnings: List[str] = []

        # Enhanced tracking
        self.user_insights: Dict[str, List[str]] = {
            "feedback_signals": [],
            "communication_style": [],
            "tool_preferences": [],
            "question_patterns": [],
            "coding_style": [],
        }
        self.tools_used: List[str] = []
        self.total_user_messages = 0
        self.total_assistant_messages = 0

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the current session and auto-extract insights"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        })

        # Track message counts
        if role == "user":
            self.total_user_messages += 1
            # Auto-analyze user messages for insights
            self._analyze_user_message(content)
        else:
            self.total_assistant_messages += 1

    def add_file_modified(self, filepath: str, change_type: str = "modified"):
        """Track files modified during this session"""
        self.files_modified.append({"file": filepath, "type": change_type})

    def add_decision(self, decision: str, rationale: str):
        """Track decisions made during session"""
        self.decisions_made.append({"decision": decision, "rationale": rationale})

    def add_learning(self, observation: str, category: str = "general"):
        """Track learnings from this session"""
        self.learnings.append({"observation": observation, "category": category})

    def generate_summary(self) -> str:
        """Generate a human-readable summary of the session"""
        duration = datetime.datetime.now() - self.session_start

        summary = [
            f"Session ID: {self.session_id[:8]}...",
            f"Date: {self.session_start.strftime('%Y-%m-%d %H:%M')}",
            f"Duration: {int(duration.total_seconds() / 60)} minutes",
            f"Messages: {len(self.messages)}",
            f"Files Modified: {len(self.files_modified)}",
            f"Decisions: {len(self.decisions_made)}",
            f"Learnings: {len(self.learnings)}",
        ]

        if self.files_modified:
            summary.append("\nFiles Modified:")
            for fm in self.files_modified:
                summary.append(f"  - {fm['file']} ({fm['type']})")

        if self.decisions_made:
            summary.append("\nDecisions Made:")
            for d in self.decisions_made:
                summary.append(f"  - {d['decision']}")

        if self.learnings:
            summary.append("\nKey Learnings:")
            for l in self.learnings:
                summary.append(f"  - {l['observation']}")

        return "\n".join(summary)

    def archive_to_db(self, topic: str = "General Session") -> str:
        """
        Archive the session to private database
        Returns: session_id for linking to dev log
        """
        print("=" * 70)
        print("Chat Archive: Saving Session to Private DB")
        print("=" * 70)

        if not self.db_path.exists():
            print(f"[ERROR] Private DB not found: {self.db_path}")
            return ""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create full conversation transcript
            transcript = self._generate_transcript()

            # Create searchable content (summary + key exchanges)
            searchable_content = self._generate_searchable_content(topic)

            # Save full transcript as document
            doc_id = str(uuid.uuid4())
            hash_val = hashlib.sha256(transcript.encode()).hexdigest()

            metadata = {
                "generated": {
                    "title": f"Chat Session: {topic} ({self.session_start.strftime('%Y-%m-%d %H:%M')})"
                },
                "session_id": self.session_id,
                "topic": topic,
                "date": self.session_start.isoformat(),
                "messages_count": len(self.messages),
                "files_modified": [fm["file"] for fm in self.files_modified],
                "decisions": [d["decision"] for d in self.decisions_made],
                "learnings": [l["observation"] for l in self.learnings],
                "tags": ["chat-archive", "session", topic.lower().replace(" ", "-")],
                "type": "conversation"
            }

            cursor.execute(
                "INSERT INTO documents (id, hash, content, metadata, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, hash_val, searchable_content, json.dumps(metadata),
                 self.session_start, datetime.datetime.now())
            )

            print(f"[OK] Saved session to private DB")
            print(f"    Session ID: {self.session_id[:8]}...")
            print(f"    Document ID: {doc_id[:8]}...")
            print(f"    Messages: {len(self.messages)}")
            print(f"    Files: {len(self.files_modified)}")

            # Also save individual important exchanges as separate searchable entries
            for decision in self.decisions_made:
                self._save_decision_to_db(cursor, decision)

            for learning in self.learnings:
                self._save_learning_to_db(cursor, learning)

            # Save auto-extracted learnings
            auto_learnings = self._extract_auto_learnings()
            print(f"\n[AUTO-ANALYSIS] Extracted {len(auto_learnings)} automatic insights:")
            for auto_learning in auto_learnings:
                self._save_learning_to_db(cursor, auto_learning)
                print(f"  - [{auto_learning['category']}] {auto_learning['observation'][:80]}...")

            conn.commit()
            conn.close()

            print(f"[OK] Session archived successfully")
            print(f"\n    Search in future sessions:")
            print(f"      rag.search('{topic}')")
            print(f"      rag.search('session {self.session_id[:8]}')")

            return self.session_id

        except Exception as e:
            print(f"[ERROR] Failed to archive: {e}")
            return ""

    def _generate_transcript(self) -> str:
        """Generate full conversation transcript"""
        lines = [
            f"# Chat Session Transcript",
            f"Session ID: {self.session_id}",
            f"Date: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Conversation",
            ""
        ]

        for msg in self.messages:
            lines.append(f"### {msg['role'].upper()} [{msg['timestamp']}]")
            lines.append(msg['content'])
            lines.append("")

        return "\n".join(lines)

    def _generate_searchable_content(self, topic: str) -> str:
        """Generate searchable summary content"""
        lines = [
            f"Chat Session: {topic}",
            f"Date: {self.session_start.strftime('%Y-%m-%d')}",
            f"Session ID: {self.session_id}",
            "",
            "## Summary",
            self.generate_summary(),
            "",
        ]

        # Add key exchanges (assistant messages only for searchability)
        if self.messages:
            lines.append("## Key Points")
            for msg in self.messages:
                if msg['role'] == 'assistant' and len(msg['content']) > 50:
                    # Extract first sentence or key point
                    preview = msg['content'][:300].replace('\n', ' ')
                    lines.append(f"- {preview}...")

        return "\n".join(lines)

    def _save_decision_to_db(self, cursor, decision: Dict):
        """Save individual decision as searchable entry"""
        doc_id = str(uuid.uuid4())
        content = f"Decision: {decision['decision']}\n\nRationale: {decision['rationale']}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()

        metadata = {
            "generated": {"title": f"Decision: {decision['decision'][:50]}..."},
            "session_id": self.session_id,
            "type": "decision",
            "tags": ["decision", "session-" + self.session_id[:8]]
        }

        cursor.execute(
            "INSERT INTO documents (id, hash, content, metadata, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, hash_val, content, json.dumps(metadata),
             datetime.datetime.now(), datetime.datetime.now())
        )

    def _save_learning_to_db(self, cursor, learning: Dict):
        """Save individual learning as searchable entry"""
        doc_id = str(uuid.uuid4())
        content = f"Learning ({learning['category']}): {learning['observation']}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()

        metadata = {
            "generated": {"title": f"Learning: {learning['observation'][:50]}..."},
            "session_id": self.session_id,
            "type": "learning",
            "category": learning['category'],
            "tags": ["learning", learning['category'], "session-" + self.session_id[:8]]
        }

        cursor.execute(
            "INSERT INTO documents (id, hash, content, metadata, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, hash_val, content, json.dumps(metadata),
             datetime.datetime.now(), datetime.datetime.now())
        )

    def update_devlog(self, devlog_path: str = "Assets/Synthesis.Pro/.devlog/DEVELOPER_LOG.md") -> bool:
        """
        Update developer log with session reference
        """
        print("\n" + "=" * 70)
        print("Updating Developer Log with Session Reference")
        print("=" * 70)

        devlog = Path(devlog_path)
        if not devlog.exists():
            print(f"[ERROR] Dev log not found: {devlog}")
            return False

        try:
            # Read current dev log
            content = devlog.read_text(encoding='utf-8')

            # Generate session entry
            date_str = self.session_start.strftime('%Y-%m-%d')
            session_entry = self._generate_devlog_entry()

            # Find the "Recently Completed" section or create it
            if "## 📝 Recently Completed Work" in content:
                # Insert after the header
                parts = content.split("## 📝 Recently Completed Work", 1)
                new_content = (
                    parts[0] +
                    "## 📝 Recently Completed Work\n\n" +
                    session_entry + "\n" +
                    parts[1]
                )
            else:
                # Add section at the end of Feature Backlog
                new_content = content + "\n\n" + "## 📝 Recently Completed Work\n\n" + session_entry

            # Write back
            devlog.write_text(new_content, encoding='utf-8')

            print(f"[OK] Updated dev log with session {self.session_id[:8]}...")
            print(f"    Files modified: {len(self.files_modified)}")
            print(f"    Decisions: {len(self.decisions_made)}")

            return True

        except Exception as e:
            print(f"[ERROR] Failed to update dev log: {e}")
            return False

    def _generate_devlog_entry(self) -> str:
        """Generate developer log entry for this session"""
        date_str = self.session_start.strftime('%Y-%m-%d')

        lines = [
            f"### {date_str} - Session {self.session_id[:8]}: Chat Archive Setup",
            ""
        ]

        if self.files_modified:
            lines.append("**Files Modified:**")
            for fm in self.files_modified:
                lines.append(f"- `{fm['file']}` ({fm['type']})")
            lines.append("")

        if self.decisions_made:
            lines.append("**Decisions Made:**")
            for d in self.decisions_made:
                lines.append(f"- {d['decision']}")
                lines.append(f"  - Rationale: {d['rationale']}")
            lines.append("")

        if self.learnings:
            lines.append("**Key Learnings:**")
            for l in self.learnings:
                lines.append(f"- [{l['category']}] {l['observation']}")
            lines.append("")

        lines.append(f"**Session ID:** `{self.session_id}` (searchable in private KB)")
        lines.append("")

        return "\n".join(lines)

    # ========== AUTO-ANALYSIS METHODS ==========

    def _analyze_user_message(self, content: str):
        """
        Automatically analyze user message to extract insights

        Extracts:
        - Feedback signals (positive/negative responses)
        - Communication style (concise/verbose, formal/casual)
        - Question patterns (what they ask about)
        - Tool preferences (tools mentioned)
        - Coding style hints
        """
        content_lower = content.lower()

        # 1. Detect feedback signals
        positive_words = ["perfect", "good", "great", "excellent", "love", "exactly", "yes", "correct", "right"]
        negative_words = ["wrong", "no", "not what", "incorrect", "bad", "broken", "doesn't work"]

        for word in positive_words:
            if word in content_lower:
                self.user_insights["feedback_signals"].append(f"POSITIVE: '{content[:100]}...'")
                break

        for word in negative_words:
            if word in content_lower:
                self.user_insights["feedback_signals"].append(f"NEGATIVE: '{content[:100]}...'")
                break

        # 2. Detect communication style
        if len(content) < 20:
            self.user_insights["communication_style"].append("concise (< 20 chars)")
        elif len(content) < 50:
            self.user_insights["communication_style"].append("brief (20-50 chars)")
        elif len(content) > 200:
            self.user_insights["communication_style"].append("detailed (> 200 chars)")

        # Check formality
        if any(word in content_lower for word in ["please", "thank", "could you"]):
            self.user_insights["communication_style"].append("polite/formal")
        elif any(word in content_lower for word in ["lol", "btw", "gonna", "wanna"]):
            self.user_insights["communication_style"].append("casual/informal")

        # 3. Detect question patterns
        if "?" in content:
            question_type = self._classify_question(content)
            self.user_insights["question_patterns"].append(f"{question_type}: {content[:80]}...")

        # 4. Detect tool mentions
        tools = ["rag", "kb", "search", "grep", "read", "edit", "write", "bash",
                 "mcp", "unity", "vfx", "devlog", "websocket"]
        for tool in tools:
            if tool in content_lower:
                if tool not in self.tools_used:
                    self.tools_used.append(tool)

        # 5. Detect coding style hints
        if "```" in content or "    " in content:  # Code block
            self.user_insights["coding_style"].append("Includes code examples in messages")

    def _classify_question(self, content: str) -> str:
        """Classify the type of question being asked"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["how do i", "how to", "how can"]):
            return "HOW_TO"
        elif any(word in content_lower for word in ["why", "what's the reason"]):
            return "WHY"
        elif any(word in content_lower for word in ["what is", "what are", "what does"]):
            return "WHAT_IS"
        elif any(word in content_lower for word in ["error", "bug", "broken", "doesn't work"]):
            return "DEBUG"
        elif any(word in content_lower for word in ["best practice", "better way", "should i"]):
            return "BEST_PRACTICE"
        else:
            return "GENERAL"

    def _extract_auto_learnings(self) -> List[Dict[str, str]]:
        """Extract learnings from auto-analyzed insights"""
        auto_learnings = []

        # Communication style learnings
        if self.user_insights["communication_style"]:
            styles = self.user_insights["communication_style"]
            concise_count = sum(1 for s in styles if "concise" in s or "brief" in s)
            verbose_count = sum(1 for s in styles if "detailed" in s)

            if concise_count > verbose_count * 2:
                auto_learnings.append({
                    "observation": "User prefers concise responses (uses brief messages)",
                    "category": "communication-style"
                })
            elif verbose_count > concise_count:
                auto_learnings.append({
                    "observation": "User provides detailed context (uses verbose messages)",
                    "category": "communication-style"
                })

            formal_count = sum(1 for s in styles if "formal" in s or "polite" in s)
            casual_count = sum(1 for s in styles if "casual" in s or "informal" in s)

            if formal_count > casual_count:
                auto_learnings.append({
                    "observation": "User communicates formally (uses polite language)",
                    "category": "communication-style"
                })
            elif casual_count > formal_count:
                auto_learnings.append({
                    "observation": "User communicates casually (informal, relaxed tone)",
                    "category": "communication-style"
                })

        # Tool preference learnings
        if self.tools_used:
            auto_learnings.append({
                "observation": f"User mentioned/used tools: {', '.join(self.tools_used)}",
                "category": "tool-usage"
            })

        # Question pattern learnings
        if self.user_insights["question_patterns"]:
            question_types = {}
            for q in self.user_insights["question_patterns"]:
                q_type = q.split(":")[0]
                question_types[q_type] = question_types.get(q_type, 0) + 1

            if question_types:
                most_common = max(question_types.items(), key=lambda x: x[1])
                auto_learnings.append({
                    "observation": f"User frequently asks {most_common[0]} questions ({most_common[1]}x this session)",
                    "category": "question-pattern"
                })

        # Feedback learnings
        if self.user_insights["feedback_signals"]:
            positive = sum(1 for f in self.user_insights["feedback_signals"] if "POSITIVE" in f)
            negative = sum(1 for f in self.user_insights["feedback_signals"] if "NEGATIVE" in f)

            if positive > 0:
                auto_learnings.append({
                    "observation": f"User gave positive feedback {positive}x this session",
                    "category": "feedback"
                })
            if negative > 0:
                auto_learnings.append({
                    "observation": f"User corrected/disagreed {negative}x this session - learn from this",
                    "category": "feedback"
                })

        # Coding style learnings
        if self.user_insights["coding_style"]:
            for style in set(self.user_insights["coding_style"]):
                auto_learnings.append({
                    "observation": style,
                    "category": "coding-style"
                })

        return auto_learnings


# Convenience function for quick archiving
def archive_session(
    topic: str,
    messages: List[Dict[str, str]],
    files_modified: List[str] = None,
    decisions: List[Dict[str, str]] = None,
    learnings: List[Dict[str, str]] = None
) -> str:
    """
    Quick archive function

    Args:
        topic: Session topic/title
        messages: List of {"role": "user|assistant", "content": "..."}
        files_modified: List of file paths
        decisions: List of {"decision": "...", "rationale": "..."}
        learnings: List of {"observation": "...", "category": "..."}

    Returns:
        session_id
    """
    archiver = ChatArchiver()

    # Add messages
    for msg in messages:
        archiver.add_message(msg["role"], msg["content"])

    # Add files
    for filepath in (files_modified or []):
        archiver.add_file_modified(filepath)

    # Add decisions
    for decision in (decisions or []):
        archiver.add_decision(decision["decision"], decision["rationale"])

    # Add learnings
    for learning in (learnings or []):
        archiver.add_learning(learning["observation"], learning.get("category", "general"))

    # Archive to DB
    session_id = archiver.archive_to_db(topic)

    # Update dev log
    if session_id:
        archiver.update_devlog()

    return session_id


if __name__ == "__main__":
    print("Chat Archiver Module - Use archive_session() to archive conversations")
