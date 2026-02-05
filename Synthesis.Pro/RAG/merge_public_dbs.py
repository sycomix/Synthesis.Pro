"""
Merge community public database with local public database
Deduplicates entries and merges new knowledge
"""
import sqlite3
import sys
from pathlib import Path

def merge_databases(local_db_path: str, community_db_path: str):
    """Merge community database into local database, deduplicating entries"""

    print(f"Merging databases...")
    print(f"  Local: {local_db_path}")
    print(f"  Community: {community_db_path}")

    try:
        # Connect to both databases
        local_conn = sqlite3.connect(local_db_path)
        community_conn = sqlite3.connect(community_db_path)

        local_cursor = local_conn.cursor()
        community_cursor = community_conn.cursor()

        # Get all documents from community DB
        community_cursor.execute("SELECT content, metadata, created_at FROM documents")
        community_docs = community_cursor.fetchall()

        # Get existing content hashes from local DB for deduplication
        local_cursor.execute("SELECT content FROM documents")
        existing_content = set(row[0] for row in local_cursor.fetchall())

        # Insert new documents that don't already exist
        new_count = 0
        for content, metadata, created_at in community_docs:
            if content not in existing_content:
                # Insert into documents table
                local_cursor.execute(
                    "INSERT INTO documents (content, metadata, created_at) VALUES (?, ?, ?)",
                    (content, metadata, created_at)
                )

                # Insert into FTS table if it exists
                try:
                    local_cursor.execute(
                        "INSERT INTO documents_fts (content, metadata) VALUES (?, ?)",
                        (content, metadata)
                    )
                except sqlite3.OperationalError:
                    pass  # FTS table doesn't exist, skip

                new_count += 1
                existing_content.add(content)  # Add to set to avoid duplicates within community DB

        local_conn.commit()

        print(f"  [OK] Merged {new_count} new entries")
        print(f"  [OK] Skipped {len(community_docs) - new_count} duplicates")

        # Close connections
        community_conn.close()
        local_conn.close()

        return new_count

    except Exception as e:
        print(f"  [ERROR] Merge failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: merge_public_dbs.py <local_db> <community_db>")
        sys.exit(1)

    local_db = sys.argv[1]
    community_db = sys.argv[2]

    if not Path(local_db).exists():
        print(f"Error: Local database not found: {local_db}")
        sys.exit(1)

    if not Path(community_db).exists():
        print(f"Error: Community database not found: {community_db}")
        sys.exit(1)

    count = merge_databases(local_db, community_db)
    sys.exit(0)
