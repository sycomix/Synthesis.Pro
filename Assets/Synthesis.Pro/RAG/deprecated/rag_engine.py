"""
DEPRECATED: This RAG engine uses sqlite-rag CLI (subprocess calls).

Use: Assets/Synthesis.Pro/RAG/core/rag_engine_lite.py instead

This file is kept for reference only. It will be removed in a future version.

Why deprecated:
- Subprocess calls to CLI are unreliable
- Complex dependencies (sqlite-rag, sqlite-vec)
- Slower than pure Python BM25S approach
- Uncomfortable for AI (CLI abstraction layer)

Migration:
  from rag_engine import SynthesisRAG  # OLD
  from core.rag_engine_lite import SynthesisRAG  # NEW

Synthesis.Pro RAG Engine (DEPRECATED)
Modern RAG system with hybrid search powered by sqlite-rag
"""

import warnings
import os
import subprocess
from typing import List, Dict, Union, Optional
from pathlib import Path

# Issue deprecation warning
warnings.warn(
    "rag_engine.py is deprecated. Use core/rag_engine_lite.py instead. "
    "This file will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)


class SynthesisRAG:
    """
    Production-grade RAG engine with hybrid search capabilities.

    Combines semantic vector search with full-text keyword search using
    Reciprocal Rank Fusion (RRF) for optimal retrieval quality.
    """

    def __init__(
        self,
        database: str = "synthesis_knowledge.db",
        private_database: Optional[str] = None,
        embedding_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Synthesis RAG engine with dual database support.

        Args:
            database: Path to public SQLite database file (Unity docs, general knowledge)
            private_database: Path to private SQLite database file (project-specific data)
                             If None, uses same as public database
            embedding_provider: "local" for sqlite-ai or "openai" for OpenAI embeddings
            model_name: Model name (for OpenAI) or path (for local)
            api_key: API key for OpenAI (if using openai provider)
        """
        self.public_database = database
        self.private_database = private_database or f"{database.replace('.db', '')}_private.db"
        self.embedding_provider = embedding_provider
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Ensure database directories exist
        for db in [self.public_database, self.private_database]:
            db_path = Path(db)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure based on provider
        if embedding_provider == "local":
            self._setup_local_embeddings()
        elif embedding_provider == "openai":
            self._setup_openai_embeddings()
        else:
            raise ValueError(f"Unknown embedding provider: {embedding_provider}")

    def _get_sqlite_rag_path(self):
        """Find the sqlite-rag executable"""
        # Try to find sqlite-rag in PATH first
        import shutil as sh
        rag_path = sh.which("sqlite-rag")
        if rag_path:
            return rag_path

        # Try to find it relative to Python executable
        import sys
        scripts_dir = Path(sys.executable).parent / "Scripts"
        rag_exe = scripts_dir / "sqlite-rag.exe"
        if rag_exe.exists():
            return str(rag_exe)

        # Unix-style
        rag_unix = scripts_dir / "sqlite-rag"
        if rag_unix.exists():
            return str(rag_unix)

        return "sqlite-rag"  # Fallback to hoping it's in PATH

    def _setup_local_embeddings(self):
        """Setup local embedding model using sqlite-ai"""
        # Check if model is downloaded
        model_name = self.model_name or "unsloth/embeddinggemma-300m-GGUF"
        model_file = "embeddinggemma-300M-Q8_0.gguf"

        # Download model if needed
        try:
            sqlite_rag = self._get_sqlite_rag_path()
            result = subprocess.run(
                [sqlite_rag, "download-model", model_name, model_file],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0 and "already exists" not in result.stdout:
                print(f"Warning: Model download issue: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError("sqlite-rag CLI not found. Install with: pip install sqlite-rag")

    def _setup_openai_embeddings(self):
        """Setup OpenAI embeddings"""
        if not self.api_key:
            raise ValueError("OpenAI API key required for 'openai' provider")

        # Configure sqlite-rag to use OpenAI
        # Note: sqlite-rag primarily uses local models
        # For OpenAI embeddings, we may need to implement custom integration
        print("Note: OpenAI embeddings require custom integration with sqlite-rag")

    def add_text(self, text: str, private: bool = True) -> bool:
        """
        Add a single text string to the knowledge base.

        WARNING: SAFETY: Defaults to PRIVATE to prevent accidental data leaks!

        Args:
            text: Text content to add
            private: If True, adds to private database; if False, adds to public database
                     DEFAULT IS TRUE for safety - only set False for public Unity docs

        Returns:
            Success status
        """
        database = self.private_database if private else self.public_database
        db_type = "PRIVATE" if private else "PUBLIC"

        # Safety check: Warn if adding to public
        if not private:
            print(f"WARNING: Adding to PUBLIC database!")
            print(f"   Make sure this content is safe to share!")

        try:
            sqlite_rag = self._get_sqlite_rag_path()

            # For large text, use temp file to avoid Windows command line length limit
            # Windows CMD has ~8191 char limit total, so use conservative threshold
            if len(text) > 2000:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
                    f.write(text)
                    temp_path = f.name

                try:
                    result = subprocess.run(
                        [sqlite_rag, "--database", database, "add", temp_path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                finally:
                    # Clean up temp file
                    import os
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            else:
                # For small text, use add-text command directly
                result = subprocess.run(
                    [sqlite_rag, "--database", database, "add-text", text],
                    capture_output=True,
                    text=True,
                    check=True
                )

            print(f"Added to {db_type} database: {database}")
            return True
        except subprocess.CalledProcessError as e:
            # Suppress verbose output for duplicate errors during migration
            if "UNIQUE constraint" not in e.stderr and "already exists" not in e.stderr:
                print(f"Error adding text to {db_type} database: {e.stderr[:200]}")
            return False
        except FileNotFoundError as e:
            # Handle Windows command line length errors - retry with temp file
            if "206" in str(e) or "filename or extension is too long" in str(e):
                print(f"Warning: Hit Windows command line limit, retrying with temp file...")
                try:
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
                        f.write(text)
                        temp_path = f.name

                    try:
                        result = subprocess.run(
                            [sqlite_rag, "--database", database, "add", temp_path],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        print(f"Added to {db_type} database: {database}")
                        return True
                    finally:
                        import os
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                except Exception as retry_error:
                    print(f"Error: Retry failed - {retry_error}")
                    return False
            else:
                print(f"FileNotFoundError: {e}")
            return False

    def add_documents(self, paths: List[str], recursive: bool = True, private: bool = True) -> bool:
        """
        Add documents from file paths to the knowledge base.

        WARNING: SAFETY: Defaults to PRIVATE to prevent accidental data leaks!

        Args:
            paths: List of file or directory paths
            recursive: Whether to process directories recursively
            private: If True, adds to private database; if False, adds to public database
                     DEFAULT IS TRUE for safety - only set False for public Unity docs

        Returns:
            Success status
        """
        database = self.private_database if private else self.public_database
        db_type = "PRIVATE" if private else "PUBLIC"

        # Safety check: Warn if adding to public
        if not private:
            print(f"WARNING:  WARNING: Adding documents to PUBLIC database!")
            print(f"   Files: {paths}")
            print(f"   Make sure these contain NO sensitive information!")
            response = input("   Continue? (yes/no): ")
            if response.lower() != "yes":
                print("ERROR: Cancelled by user")
                return False

        try:
            sqlite_rag = self._get_sqlite_rag_path()
            for path in paths:
                cmd = [sqlite_rag, "--database", database, "add", path]
                if recursive:
                    cmd.append("--recursive")

                print(f"Adding {path} to {db_type} database...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
            print(f"Documents added to {db_type} database: {database}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error adding documents to {db_type} database: {e.stderr}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 5,
        search_type: str = "hybrid",
        scope: str = "both"
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Search the knowledge base using hybrid search.

        Args:
            query: Search query
            top_k: Number of results to return
            search_type: "hybrid", "vector", or "fts" (full-text search)
            scope: "public", "private", or "both" - which database(s) to search

        Returns:
            List of search results with text, scores, and source (public/private)
        """
        all_results = []

        # Determine which databases to search
        databases = []
        if scope in ["public", "both"]:
            databases.append(("public", self.public_database))
        if scope in ["private", "both"]:
            databases.append(("private", self.private_database))

        # Search each database
        sqlite_rag = self._get_sqlite_rag_path()
        for source, database in databases:
            try:
                cmd = [
                    sqlite_rag,
                    "--database", database,
                    "search", query,
                    "--limit", str(top_k)
                ]

                if search_type != "hybrid":
                    cmd.extend(["--search-type", search_type])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Parse results
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        all_results.append({
                            "text": line,
                            "score": 1.0,  # sqlite-rag may not return scores in CLI output
                            "source": source  # Mark which database this came from
                        })

            except subprocess.CalledProcessError as e:
                print(f"Error searching {source} database: {e.stderr}")

        # If searching both, we already have results from each
        # Limit to top_k total results
        return all_results[:top_k]

    def add_ai_note(self, note: str, category: str = "general") -> bool:
        """
        Add an AI internal note to the private database.

        Use this for AI reasoning, analysis, patterns discovered, etc.
        This keeps AI thoughts separate from user data.

        Args:
            note: The AI's internal note/thought
            category: Category for organization (e.g., "analysis", "pattern", "todo")

        Returns:
            Success status
        """
        formatted_note = f"[AI-NOTE:{category}] {note}"
        return self.add_text(formatted_note, private=True)

    def add_project_data(self, data: str, description: str = "") -> bool:
        """
        Add project-specific data to the private database.

        Use this for code snippets, configs, project-specific knowledge.

        Args:
            data: The project data
            description: Optional description of the data

        Returns:
            Success status
        """
        if description:
            formatted = f"[PROJECT] {description}\n{data}"
        else:
            formatted = f"[PROJECT] {data}"
        return self.add_text(formatted, private=True)

    def add_user_preference(self, preference: str, context: str = "") -> bool:
        """
        Track user preferences and working style in the private database.

        Use this to remember how the user likes to work, their preferences,
        coding style, communication patterns, etc.

        Args:
            preference: The user preference or pattern
            context: Additional context about when/why this matters

        Returns:
            Success status
        """
        if context:
            formatted = f"[USER-PREFERENCE] {preference} | Context: {context}"
        else:
            formatted = f"[USER-PREFERENCE] {preference}"
        return self.add_text(formatted, private=True)

    def add_project_context(self, event: str, decision: str = "") -> bool:
        """
        Track project history, decisions, and context in the private database.

        Use this to remember important project milestones, architectural decisions,
        why certain choices were made, etc.

        Args:
            event: The event or decision
            decision: Why this decision was made (rationale)

        Returns:
            Success status
        """
        if decision:
            formatted = f"[PROJECT-CONTEXT] {event} | Rationale: {decision}"
        else:
            formatted = f"[PROJECT-CONTEXT] {event}"
        return self.add_text(formatted, private=True)

    def add_relationship_note(self, note: str) -> bool:
        """
        Track notes about the AI-user working relationship.

        Use this for communication patterns, collaboration insights,
        what works well, what to avoid, etc.

        Args:
            note: Relationship/collaboration note

        Returns:
            Success status
        """
        formatted = f"[RELATIONSHIP] {note}"
        return self.add_text(formatted, private=True)

    def add_public_solution(self, problem: str, solution: str, tags: str = "") -> bool:
        """
        Add an anonymous code solution to the PUBLIC database.

        WARNING: IMPORTANT: Sanitize before adding! Remove:
        - Project-specific names
        - API keys, credentials
        - Business logic
        - Proprietary algorithms

        Use this for reusable Asset Store integrations, anonymous code examples,
        and generic issue solutions that can help others.

        Args:
            problem: Description of the problem (anonymous)
            solution: The solution code/approach (sanitized)
            tags: Optional tags (e.g., "Unity, Asset Store, TextMeshPro")

        Returns:
            Success status
        """
        formatted = f"[SOLUTION] Problem: {problem}\n"
        if tags:
            formatted += f"Tags: {tags}\n"
        formatted += f"Solution:\n{solution}"

        return self.add_text(formatted, private=False)

    # ========== Efficiency Helper Methods ==========
    # Quick logging methods to reduce ceremony and encourage frequent use

    def quick_note(self, note: str) -> bool:
        """
        Ultra-fast note taking. No ceremony, just log it.

        Args:
            note: The note (will be timestamped automatically)

        Returns:
            Success status

        Example:
            rag.quick_note("User prefers tabs over spaces")
            rag.quick_note("Bug in PlayerController line 47")
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted = f"[QUICK-NOTE:{timestamp}] {note}"
        return self.add_text(formatted, private=True)

    def log_decision(self, what: str, why: str = "", alternatives: str = "") -> bool:
        """
        Log an architectural or design decision.

        Args:
            what: The decision made
            why: Rationale for the decision
            alternatives: Other options considered

        Returns:
            Success status

        Example:
            rag.log_decision(
                what="Using WebSocket instead of HTTP polling",
                why="Real-time bidirectional communication needed",
                alternatives="HTTP long-polling, Server-Sent Events"
            )
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d")
        formatted = f"[DECISION:{timestamp}] {what}"
        if why:
            formatted += f"\nRationale: {why}"
        if alternatives:
            formatted += f"\nAlternatives considered: {alternatives}"
        return self.add_text(formatted, private=True)

    def checkpoint(self, phase: str, status: str, next_steps: str = "") -> bool:
        """
        Quick project checkpoint/milestone marker.

        Args:
            phase: Phase or feature name
            status: Current status
            next_steps: What's next (optional)

        Returns:
            Success status

        Example:
            rag.checkpoint(
                phase="Phase 2: WebSocket Layer",
                status="COMPLETE",
                next_steps="Phase 3: AI Integration"
            )
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted = f"[CHECKPOINT:{timestamp}] {phase} - {status}"
        if next_steps:
            formatted += f"\nNext: {next_steps}"
        return self.add_text(formatted, private=True)

    def log_efficiency_win(self, what: str, saved: str) -> bool:
        """
        Track efficiency improvements and optimizations.

        Args:
            what: What was optimized
            saved: What was saved (time, tokens, cost)

        Returns:
            Success status

        Example:
            rag.log_efficiency_win(
                what="Store project status in RAG instead of re-reading files",
                saved="~34K tokens per session"
            )
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d")
        formatted = f"[EFFICIENCY:{timestamp}] {what}\nSavings: {saved}"
        return self.add_text(formatted, private=True)

    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Get database statistics for both public and private databases.

        Returns:
            Dictionary with stats for each database
        """
        # This would require direct SQLite access or a stats command
        # Placeholder implementation
        return {
            "public": {
                "database": self.public_database,
                "documents": 0,
                "chunks": 0,
                "embeddings": 0
            },
            "private": {
                "database": self.private_database,
                "documents": 0,
                "chunks": 0,
                "embeddings": 0
            }
        }

    def audit_public_database(self) -> Dict[str, any]:
        """
        Audit the PUBLIC database for potentially sensitive content.

        Scans for:
        - API keys, tokens, passwords, secrets
        - Project-specific names
        - Personal information
        - Configuration details that should be private

        Returns:
            Dictionary with audit results and flagged entries
        """
        import sqlite3
        import re

        results = {
            "total_documents": 0,
            "flagged_count": 0,
            "flagged_entries": [],
            "warnings": [],
            "passed": True
        }

        # Sensitive patterns to check for
        sensitive_patterns = [
            (r'(?i)(api[_\s-]?key|apikey)', "API Key reference"),
            (r'(?i)(secret|password|passwd|pwd)', "Secret/Password reference"),
            (r'(?i)(token|auth[_\s-]?token)', "Token reference"),
            (r'(?i)(credential)', "Credential reference"),
            (r'(?i)(private[_\s-]?key)', "Private key reference"),
            (r'[a-zA-Z0-9]{20,}', "Potential API key/token (long alphanumeric)"),
            (r'(?i)(config\.json|settings\.ini|\.env)', "Configuration file reference"),
            (r'(?i)(database[_\s-]?connection|connection[_\s-]?string)', "Database connection reference"),
            (r'(?i)(localhost:\d+|127\.0\.0\.1:\d+|192\.168\.\d+\.\d+)', "Local network address"),
            (r'(?i)(username|user[_\s-]?id|email)', "User identification"),
        ]

        try:
            db_path = Path(self.public_database)
            if not db_path.exists():
                results["warnings"].append("Public database does not exist yet")
                return results

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            results["total_documents"] = cursor.fetchone()[0]

            # Scan each document
            cursor.execute("SELECT id, path, content FROM documents")
            rows = cursor.fetchall()

            for row_id, path, content in rows:
                if not content:
                    continue

                content_str = str(content)
                flags = []

                # Check against each pattern
                for pattern, description in sensitive_patterns:
                    if re.search(pattern, content_str):
                        flags.append(description)

                # If content has flags, add to flagged entries
                if flags:
                    results["flagged_count"] += 1
                    results["flagged_entries"].append({
                        "id": row_id,
                        "path": path or "Unknown",
                        "flags": flags,
                        "preview": content_str[:150] + "..." if len(content_str) > 150 else content_str
                    })

            conn.close()

            # Determine if audit passed
            if results["flagged_count"] > 0:
                results["passed"] = False
                results["warnings"].append(
                    f"Found {results['flagged_count']} potentially sensitive entries in PUBLIC database"
                )
            else:
                results["warnings"].append("No obvious sensitive content detected")

        except Exception as e:
            results["passed"] = False
            results["warnings"].append(f"Audit error: {str(e)}")

        return results

    def clear_database(self) -> bool:
        """
        Clear all data from the database.

        Returns:
            Success status
        """
        try:
            db_path = Path(self.database)
            if db_path.exists():
                db_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False


# Backward compatibility with old RAG interface
class RAGEngine(SynthesisRAG):
    """Alias for backward compatibility"""
    pass


if __name__ == "__main__":
    # Example usage demonstrating dual database (public/private)
    print("=" * 60)
    print("Initializing Synthesis.Pro RAG Engine (Dual Database)")
    print("=" * 60)

    # Create RAG instance with separate public and private databases
    rag = SynthesisRAG(
        database="test_public.db",           # Public: Unity docs, tutorials
        private_database="test_private.db",  # Private: project data, AI notes
        embedding_provider="local"
    )

    print("\nPUBLIC DATABASE (Safe to share)")
    print("-" * 60)
    # Add public knowledge (Unity documentation, etc.)
    rag.add_text("Unity uses C# for scripting.", private=False)
    rag.add_text("GameObjects are the base class for all scene objects.", private=False)

    print("\nPRIVATE DATABASE (Confidential)")
    print("-" * 60)
    # Add private project data (defaults to private=True for safety)
    rag.add_project_data("PlayerController handles input and movement")
    rag.add_project_data("API key stored in config.json", "Config location")

    # AI can store internal notes
    rag.add_ai_note("User prefers coroutines over async/await", category="pattern")
    rag.add_ai_note("Bug in PlayerController line 47 needs review", category="todo")

    print("\nSEARCHING")
    print("-" * 60)

    # Search public only
    print("\n1. Public search (Unity):")
    results = rag.search("Unity scripting", top_k=2, scope="public")
    for i, result in enumerate(results, 1):
        print(f"   [{result['source']}] {result['text']}")

    # Search private only
    print("\n2. Private search (project):")
    results = rag.search("PlayerController", top_k=2, scope="private")
    for i, result in enumerate(results, 1):
        print(f"   [{result['source']}] {result['text']}")

    # Search both (default)
    print("\n3. Combined search (both databases):")
    results = rag.search("Unity player", top_k=3, scope="both")
    for i, result in enumerate(results, 1):
        print(f"   [{result['source']}] {result['text']}")

    print("\n" + "=" * 60)
    print("SUCCESS: Synthesis.Pro Dual Database Demo Complete!")
    print("=" * 60)
    print("\nKey Benefits:")
    print("  • Public DB: Safe Unity docs, shareable knowledge")
    print("  • Private DB: Project data, AI notes, sensitive info")
    print("  • Safety: Defaults to private to prevent leaks")
    print("  • Flexibility: Search one or both databases")
