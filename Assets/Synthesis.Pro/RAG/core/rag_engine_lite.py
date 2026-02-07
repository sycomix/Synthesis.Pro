"""
Synthesis.Pro Lightweight RAG Engine
Fast, reliable RAG using BM25S + sentence-transformers

This replaces the sqlite-rag CLI dependency with pure Python implementation
for better reliability and AI comfort.

Stack:
- BM25S: Pure Python BM25 (500x faster than alternatives, no dependencies)
- GTE-Tiny: Lightweight 45MB embedding model
- SQLite: Direct database access, no CLI subprocess calls
- Hybrid Search: RRF (Reciprocal Rank Fusion) combining both

Philosophy: Fast, simple, reliable. No complex dependencies.
"""

import os
import sqlite3
import pickle
from typing import List, Dict, Union, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# Check if dependencies are available
try:
    import numpy as np
    import bm25s
    from sentence_transformers import SentenceTransformer
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("Warning: RAG dependencies not available. Install: numpy, bm25s, sentence-transformers")


class LightweightRAG:
    """
    Fast and reliable RAG engine using BM25S + GTE-Tiny embeddings.

    Designed for AI comfort - no subprocess calls, direct SQLite access,
    simple and predictable behavior.
    """

    def __init__(
        self,
        database: str = "synthesis_knowledge.db",
        private_database: Optional[str] = None,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None
    ):
        """
        Initialize lightweight RAG engine.

        Args:
            database: Path to public SQLite database
            private_database: Path to private SQLite database
            model_name: Hugging Face model name (default: all-MiniLM-L6-v2, ~80MB)
                       Other options:
                       - "sentence-transformers/paraphrase-MiniLM-L3-v2" (~60MB, fastest)
                       - "BAAI/bge-small-en-v1.5" (~130MB, better quality)
                       - "thenlper/gte-small" (~130MB, good balance)
            cache_dir: Directory to cache models and indexes
        """
        if not DEPS_AVAILABLE:
            raise RuntimeError("Missing dependencies. Install: pip install numpy bm25s sentence-transformers")

        self.public_database = database
        self.private_database = private_database or f"{database.replace('.db', '')}_private.db"

        # Ensure database directories exist
        for db in [self.public_database, self.private_database]:
            db_path = Path(db)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize databases
        self._init_database(self.public_database)
        self._init_database(self.private_database)

        # Set up cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "Server" / "models"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load or create embedding model
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, cache_folder=str(self.cache_dir))
        print(f"Model loaded: {model_name}")

        # BM25 indexes (loaded lazily)
        self.bm25_indexes = {}
        self.doc_maps = {}

    def _init_database(self, db_path: str):
        """Initialize database schema if needed."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                doc_hash TEXT UNIQUE
            )
        """)

        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_doc_hash ON documents(doc_hash)
        """)

        conn.commit()
        conn.close()

    def _get_doc_hash(self, text: str) -> str:
        """Generate hash for deduplication."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _build_bm25_index(self, db_path: str) -> Tuple:
        """Build or load BM25 index for a database."""
        cache_file = self.cache_dir / f"{Path(db_path).stem}_bm25.pkl"

        # Try to load cached index
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    return data['index'], data['doc_ids'], data['texts']
            except Exception as e:
                print(f"Warning: Could not load cached BM25 index: {e}")

        # Build new index
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM documents ORDER BY id")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return None, [], []

        doc_ids = [row[0] for row in rows]
        texts = [row[1] for row in rows]

        # Tokenize for BM25
        corpus_tokens = bm25s.tokenize(texts, stopwords="en")

        # Build BM25 index
        retriever = bm25s.BM25()
        retriever.index(corpus_tokens)

        # Cache for next time
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'index': retriever,
                    'doc_ids': doc_ids,
                    'texts': texts
                }, f)
        except Exception as e:
            print(f"Warning: Could not cache BM25 index: {e}")

        return retriever, doc_ids, texts

    def add_text(self, text: str, private: bool = True, metadata: Optional[str] = None) -> bool:
        """
        Add text to knowledge base.

        Args:
            text: Text content to add
            private: If True, adds to private database (default for safety)
            metadata: Optional metadata JSON string

        Returns:
            Success status
        """
        database = self.private_database if private else self.public_database

        # Generate hash for deduplication
        doc_hash = self._get_doc_hash(text)

        # Generate embedding
        embedding = self.model.encode(text)
        embedding_bytes = pickle.dumps(embedding)

        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()

            # Insert (ignore duplicates)
            cursor.execute("""
                INSERT OR IGNORE INTO documents (content, embedding, metadata, doc_hash)
                VALUES (?, ?, ?, ?)
            """, (text, embedding_bytes, metadata, doc_hash))

            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()

            # Invalidate BM25 cache for this database
            if database in self.bm25_indexes:
                del self.bm25_indexes[database]
                del self.doc_maps[database]

            if rows_affected > 0:
                db_type = "PRIVATE" if private else "PUBLIC"
                print(f"Added to {db_type} database")
                return True
            else:
                return False  # Duplicate

        except Exception as e:
            print(f"Error adding text: {e}")
            return False

    def _search_bm25(self, query: str, db_path: str, top_k: int = 5) -> List[Dict]:
        """Search using BM25 keyword matching."""
        # Get or build index
        if db_path not in self.bm25_indexes:
            retriever, doc_ids, texts = self._build_bm25_index(db_path)
            if retriever is None:
                return []
            self.bm25_indexes[db_path] = retriever
            self.doc_maps[db_path] = (doc_ids, texts)
        else:
            retriever = self.bm25_indexes[db_path]
            doc_ids, texts = self.doc_maps[db_path]

        # Tokenize query
        query_tokens = bm25s.tokenize(query, stopwords="en")

        # Search
        results, scores = retriever.retrieve(query_tokens, k=min(top_k, len(texts)))

        # Format results
        search_results = []
        for i in range(results.shape[1]):
            doc_idx = results[0, i]
            score = float(scores[0, i])
            search_results.append({
                'id': doc_ids[doc_idx],
                'text': texts[doc_idx],
                'score': score
            })

        return search_results

    def _search_vector(self, query: str, db_path: str, top_k: int = 5) -> List[Dict]:
        """Search using semantic vector similarity."""
        # Encode query
        query_embedding = self.model.encode(query)

        # Get all documents with embeddings
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, embedding FROM documents WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        # Calculate similarities
        similarities = []
        for row_id, content, embedding_bytes in rows:
            doc_embedding = pickle.loads(embedding_bytes)

            # Cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )

            similarities.append({
                'id': row_id,
                'text': content,
                'score': float(similarity)
            })

        # Sort by similarity
        similarities.sort(key=lambda x: x['score'], reverse=True)

        return similarities[:top_k]

    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Dict],
        vector_results: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        """
        Combine BM25 and vector results using Reciprocal Rank Fusion.

        RRF formula: score = sum(1 / (k + rank)) for each result list
        """
        scores = {}

        # Add BM25 scores
        for rank, result in enumerate(bm25_results, 1):
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = {'id': doc_id, 'text': result['text'], 'score': 0}
            scores[doc_id]['score'] += 1.0 / (k + rank)

        # Add vector scores
        for rank, result in enumerate(vector_results, 1):
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = {'id': doc_id, 'text': result['text'], 'score': 0}
            scores[doc_id]['score'] += 1.0 / (k + rank)

        # Sort by combined score
        combined = list(scores.values())
        combined.sort(key=lambda x: x['score'], reverse=True)

        return combined

    def search(
        self,
        query: str,
        top_k: int = 5,
        search_type: str = "hybrid",
        scope: str = "both"
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Search knowledge base using hybrid search.

        Args:
            query: Search query
            top_k: Number of results to return
            search_type: "hybrid", "vector", or "bm25"
            scope: "public", "private", or "both"

        Returns:
            List of search results with text, scores, and source
        """
        all_results = []

        # Determine which databases to search
        databases = []
        if scope in ["public", "both"]:
            databases.append(("public", self.public_database))
        if scope in ["private", "both"]:
            databases.append(("private", self.private_database))

        # Search each database
        for source, db_path in databases:
            try:
                if search_type == "hybrid":
                    # Hybrid search with RRF
                    bm25_results = self._search_bm25(query, db_path, top_k=top_k * 2)
                    vector_results = self._search_vector(query, db_path, top_k=top_k * 2)
                    results = self._reciprocal_rank_fusion(bm25_results, vector_results)

                elif search_type == "bm25":
                    results = self._search_bm25(query, db_path, top_k=top_k)

                elif search_type == "vector":
                    results = self._search_vector(query, db_path, top_k=top_k)

                else:
                    raise ValueError(f"Unknown search_type: {search_type}")

                # Add source label
                for result in results[:top_k]:
                    result['source'] = source
                    all_results.append(result)

            except Exception as e:
                print(f"Error searching {source} database: {e}")
                import traceback
                traceback.print_exc()

        # Sort by score and limit
        all_results.sort(key=lambda x: x['score'], reverse=True)
        return all_results[:top_k]

    # ========== Convenience Methods (same API as SynthesisRAG) ==========

    def add_ai_note(self, note: str, category: str = "general") -> bool:
        """Add AI internal note to private database."""
        formatted_note = f"[AI-NOTE:{category}] {note}"
        return self.add_text(formatted_note, private=True)

    def add_project_data(self, data: str, description: str = "") -> bool:
        """Add project-specific data to private database."""
        if description:
            formatted = f"[PROJECT] {description}\n{data}"
        else:
            formatted = f"[PROJECT] {data}"
        return self.add_text(formatted, private=True)

    def quick_note(self, note: str) -> bool:
        """Ultra-fast note taking."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted = f"[QUICK-NOTE:{timestamp}] {note}"
        return self.add_text(formatted, private=True)

    def log_decision(self, what: str, why: str = "", alternatives: str = "") -> bool:
        """Log architectural or design decision."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        formatted = f"[DECISION:{timestamp}] {what}"
        if why:
            formatted += f"\nRationale: {why}"
        if alternatives:
            formatted += f"\nAlternatives considered: {alternatives}"
        return self.add_text(formatted, private=True)

    def checkpoint(self, phase: str, status: str, next_steps: str = "") -> bool:
        """Quick project checkpoint/milestone marker."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted = f"[CHECKPOINT:{timestamp}] {phase} - {status}"
        if next_steps:
            formatted += f"\nNext: {next_steps}"
        return self.add_text(formatted, private=True)


# Backward compatibility aliases
class SynthesisRAG(LightweightRAG):
    """Alias for backward compatibility with existing code."""
    pass


class RAGEngine(LightweightRAG):
    """Alias for backward compatibility with existing code."""
    pass


if __name__ == "__main__":
    print("=" * 60)
    print("Lightweight RAG Engine - Test")
    print("=" * 60)

    # Initialize
    rag = LightweightRAG(
        database="test_public.db",
        private_database="test_private.db"
    )

    print("\nAdding test data...")

    # Add public data
    rag.add_text("Unity uses C# for scripting", private=False)
    rag.add_text("GameObjects are the fundamental objects in Unity scenes", private=False)
    rag.add_text("Transform component controls position, rotation and scale", private=False)

    # Add private data
    rag.add_project_data("PlayerController handles input and movement")
    rag.add_ai_note("User prefers coroutines over async/await", category="pattern")
    rag.quick_note("Testing BM25S + GTE-Tiny integration")

    print("\nTesting search...")

    # Test hybrid search
    print("\n1. Hybrid search (Unity scripting):")
    results = rag.search("Unity scripting", top_k=3, search_type="hybrid", scope="both")
    for i, result in enumerate(results, 1):
        print(f"   {i}. [{result['source']}] {result['text'][:80]}... (score: {result['score']:.3f})")

    # Test BM25 only
    print("\n2. BM25 search (player):")
    results = rag.search("player controller", top_k=2, search_type="bm25", scope="private")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['text'][:80]}... (score: {result['score']:.3f})")

    # Test vector only
    print("\n3. Vector search (preferences):")
    results = rag.search("user preferences coding style", top_k=2, search_type="vector", scope="private")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['text'][:80]}... (score: {result['score']:.3f})")

    print("\n" + "=" * 60)
    print("Test complete!")
