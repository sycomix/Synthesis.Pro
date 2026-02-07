#!/usr/bin/env python3
"""
Quick RAG Query Tool for Claude Code
Allows AI to search the knowledge base naturally
"""
import sys
import sqlite3
import json
from pathlib import Path

def query_kb(search_term: str, limit: int = 5, use_private: bool = True):
    """Search knowledge base and return results"""

    # Determine database path
    db_name = "synthesis_private.db" if use_private else "synthesis_public.db"
    db_path = Path(__file__).parent / "Assets" / "Synthesis.Pro" / "Server" / db_name

    if not db_path.exists():
        return {"error": f"Database not found: {db_path}", "results": []}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Full-text search using FTS5
        cursor.execute("""
            SELECT d.content, d.metadata, d.created_at
            FROM documents d
            JOIN documents_fts ON documents_fts.rowid = d.id
            WHERE documents_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (search_term, limit))

        results = cursor.fetchall()
        conn.close()

        return {
            "success": True,
            "query": search_term,
            "database": db_name,
            "results": [
                {
                    "content": content,
                    "metadata": json.loads(metadata) if metadata else {},
                    "created_at": created_at
                }
                for content, metadata, created_at in results
            ]
        }

    except Exception as e:
        return {"error": str(e), "results": []}

def get_stats():
    """Get knowledge base statistics"""
    stats = {}

    for db_name in ["synthesis_private.db", "synthesis_public.db"]:
        db_path = Path(__file__).parent / "Assets" / "Synthesis.Pro" / "Server" / db_name

        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM documents")
                count = cursor.fetchone()[0]

                cursor.execute("SELECT value FROM metadata WHERE key = 'db_type'")
                db_type = cursor.fetchone()

                conn.close()

                stats[db_name] = {
                    "exists": True,
                    "document_count": count,
                    "type": db_type[0] if db_type else "unknown",
                    "size": f"{db_path.stat().st_size / 1024:.1f} KB"
                }
            except Exception as e:
                stats[db_name] = {"exists": True, "error": str(e)}
        else:
            stats[db_name] = {"exists": False}

    return stats

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps(get_stats(), indent=2))
        sys.exit(0)

    command = sys.argv[1]

    if command == "stats":
        print(json.dumps(get_stats(), indent=2))
    elif command == "search":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: rag_query.py search <term>"}, indent=2))
            sys.exit(1)

        search_term = " ".join(sys.argv[2:])
        result = query_kb(search_term)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}, indent=2))
