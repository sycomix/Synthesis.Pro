"""
Quick RAG query tool for Claude Code to access knowledge base
Usage: python quick_query.py "your search query here"
"""
import sys
import sqlite3
from pathlib import Path

def search_kb(query: str, limit: int = 5):
    """Search the private knowledge base using FTS"""

    # Database path
    db_path = Path(__file__).parent.parent / "Server" / "synthesis_private.db"

    if not db_path.exists():
        print(f"Error: Knowledge base not found at {db_path}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Search using FTS (Full-Text Search)
        cursor.execute("""
            SELECT d.content, d.metadata, d.created_at
            FROM documents d
            JOIN documents_fts ON documents_fts.rowid = d.id
            WHERE documents_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        results = cursor.fetchall()

        if not results:
            print(f"No results found for: {query}")
            return

        print("=" * 70)
        print(f"Search Results for: {query}")
        print("=" * 70)
        print()

        for i, (content, metadata, created_at) in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"Created: {created_at}")
            if metadata:
                print(f"Metadata: {metadata}")
            print(f"Content: {content[:500]}{'...' if len(content) > 500 else ''}")
            print("-" * 70)
            print()

        conn.close()

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("Error: Knowledge base not initialized. Run init_databases.py first.")
        else:
            print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_query.py 'your search query'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    search_kb(query)
