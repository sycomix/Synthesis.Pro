"""
Simple KB query - no FTS required
Usage: python simple_query.py "search term"
"""
import sys
import sqlite3
from pathlib import Path

def search_kb(search_term: str):
    """Search knowledge base using LIKE"""

    db_path = Path(__file__).parent.parent / "Server" / "synthesis_private.db"

    if not db_path.exists():
        print(f"Error: DB not found")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # First, show what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Available tables: {', '.join(tables)}")
        print("=" * 70)
        print()

        # Try to find and search the main content table
        if 'documents' in tables:
            cursor.execute("""
                SELECT content, metadata, created_at
                FROM documents
                WHERE content LIKE ? OR metadata LIKE ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (f"%{search_term}%", f"%{search_term}%"))

            results = cursor.fetchall()

            if not results:
                print(f"No results for: {search_term}")
                return

            for i, (content, metadata, created_at) in enumerate(results, 1):
                print(f"\n[Result {i}] {created_at}")
                if metadata:
                    print(f"Meta: {metadata[:100]}")
                # Show first 300 chars
                preview = content[:300].replace('\n', ' ')
                print(f"Content: {preview}...")
                print("-" * 70)

        elif 'chat_sessions' in tables or 'sessions' in tables:
            table = 'chat_sessions' if 'chat_sessions' in tables else 'sessions'
            cursor.execute(f"""
                SELECT * FROM {table}
                LIMIT 5
            """)
            results = cursor.fetchall()
            print(f"\nFound {len(results)} entries in {table}")
            for row in results:
                print(row[:3] if len(row) > 3 else row)

        else:
            print("No recognizable content tables found")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    term = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "session"
    search_kb(term)
