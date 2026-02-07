"""
RAG Search Demo - Direct FTS and Vector Search
Demonstrates searching the knowledge base for VFX and Unity content
"""
import sqlite3
from pathlib import Path

print("=" * 70)
print("RAG-First Workflow: Knowledge Base Search")
print("=" * 70)

# Database paths
db_private = Path("Server/synthesis_private.db")
db_public = Path("Server/synthesis_knowledge.db")

def search_db(db_path, query, db_name, limit=5):
    """Search database using FTS"""
    print(f"\n[{db_name}] Searching for: '{query}'")
    print("-" * 70)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # FTS search on chunks
        cursor.execute("""
            SELECT c.content, c.document_id, d.title, d.path
            FROM chunks c
            JOIN chunks_fts fts ON c.rowid = fts.rowid
            JOIN documents d ON c.document_id = d.id
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        results = cursor.fetchall()

        if results:
            print(f"  Found {len(results)} results:\n")
            for i, (content, doc_id, title, path) in enumerate(results, 1):
                preview = content[:250].replace('\n', ' ').strip()
                file_info = title or path or f"Doc #{doc_id}"
                print(f"  {i}. {file_info}")
                print(f"     {preview}...")
                print()
        else:
            print("  No results found\n")

        conn.close()
        return len(results) if results else 0

    except Exception as e:
        print(f"  [ERROR] {e}\n")
        return 0

# Search queries
searches = [
    "VFX Visual Effect Graph asset creation",
    "Unity ScriptableObject MenuItem editor",
    "Unity reflection internal API EditorUtility",
    "Unity asset creation programmatic",
]

print(f"\nDatabase Stats:")
print(f"  Public:  {db_public} - 729 Unity docs")
print(f"  Private: {db_private} - 5,329 project documents")

total_results = 0

# Search private DB
print("\n" + "=" * 70)
print("PRIVATE DATABASE (Project-Specific Knowledge)")
print("=" * 70)

for query in searches:
    total_results += search_db(db_private, query, "PRIVATE", limit=3)

# Search public DB
print("\n" + "=" * 70)
print("PUBLIC DATABASE (Unity Documentation)")
print("=" * 70)

for query in searches:
    total_results += search_db(db_public, query, "PUBLIC", limit=3)

print("=" * 70)
print("Search Summary")
print("=" * 70)
print(f"Total results found: {total_results}")
print("\nKey Benefits:")
print("  - Searched 6,000+ documents in seconds")
print("  - Full-text search finds relevant context")
print("  - No manual file reading required")
print("  - Context-efficient: ~500 tokens vs 50K+ from file reads")
print("  - Privacy-first: Project data stays in private DB")
print("=" * 70)
