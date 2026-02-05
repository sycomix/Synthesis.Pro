"""
Add knowledge to public database
Usage: python add_knowledge.py "content here" "optional metadata"
"""
import sys
import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime

def add_to_public_kb(content: str, metadata: dict = None):
    """Add entry to public knowledge base"""

    # Try both names (synthesis_public.db is the new name, synthesis_knowledge.db is legacy)
    db_path = Path(__file__).parent.parent / "Server" / "synthesis_public.db"
    if not db_path.exists():
        db_path = Path(__file__).parent.parent / "Server" / "synthesis_knowledge.db"

    if not db_path.exists():
        print(f"Error: Public DB not found at {db_path}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Add to documents table
        meta_json = json.dumps(metadata) if metadata else '{}'
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        doc_id = f"doc_{content_hash[:16]}"

        cursor.execute(
            "INSERT INTO documents (id, hash, content, metadata) VALUES (?, ?, ?, ?)",
            (doc_id, content_hash, content, meta_json)
        )


        # Add to FTS if table exists
        try:
            cursor.execute(
                "INSERT INTO documents_fts (content, metadata) VALUES (?, ?)",
                (content, meta_json or "")
            )
        except sqlite3.OperationalError:
            pass  # FTS table doesn't exist

        conn.commit()
        conn.close()

        print(f"[OK] Added to public KB (doc_id: {doc_id})")
        return doc_id

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_knowledge.py 'content' '{\"key\":\"value\"}'")
        sys.exit(1)

    content = sys.argv[1]
    metadata = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None

    add_to_public_kb(content, metadata)
