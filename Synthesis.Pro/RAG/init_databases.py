"""
Initialize Synthesis.Pro RAG databases
Creates empty public and private databases for immediate use
"""
import sqlite3
import sys
from pathlib import Path

print("=" * 70)
print("Initializing Synthesis.Pro RAG Databases")
print("=" * 70)

# Database paths
server_dir = Path(__file__).parent.parent / "Server"
public_db = server_dir / "synthesis_public.db"
private_db = server_dir / "synthesis_private.db"

def init_database(db_path: Path, db_type: str):
    """Initialize a RAG database with basic schema"""
    print(f"\n[{db_type}] Initializing: {db_path}")

    try:
        # Create connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create documents table (basic structure for sqlite-rag compatibility)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create FTS virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
            USING fts5(content, metadata)
        """)

        # Create embeddings table for vector search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY,
                document_id INTEGER NOT NULL,
                embedding BLOB,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)

        # Create metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert database type and version
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value)
            VALUES ('db_type', ?), ('version', '1.0.0'), ('initialized_at', datetime('now'))
        """, (db_type,))

        conn.commit()

        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"  [OK] Created {len(tables)} tables: {', '.join(tables)}")

        conn.close()
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to initialize: {e}")
        return False

# Initialize both databases
print("\nCreating database files...")
success = True
private_db_created = False

if not public_db.exists():
    success &= init_database(public_db, "public")
else:
    print(f"\n[PUBLIC] Already exists: {public_db}")

if not private_db.exists():
    private_db_created = True
    success &= init_database(private_db, "private")
else:
    print(f"\n[PRIVATE] Already exists: {private_db} - PRESERVING SACRED DATA")

# Add initial entry to private DB ONLY if we just created it
if success and private_db_created:
    print("\n" + "=" * 70)
    print("Adding VFX investigation findings to private DB...")
    try:
        conn = sqlite3.connect(private_db)
        cursor = conn.cursor()

        # Add the VFX issue as first entry
        findings = [
            (
                "VFX Asset Creation Issue - ManageVFX.cs:216",
                '{"type": "code_issue", "file": "ManageVFX.cs", "line": 216, '
                '"category": "unity_api", "date": "2026-02-02"}'
            ),
            (
                "VFX asset creation currently uses reflection to access internal Unity APIs "
                "(VisualEffectAssetEditorUtility.CreateNewAsset and VisualEffectResource.CreateNewAsset). "
                "Need to find authenticated/public API approach. Decision: Using reflection due to no public "
                "Unity API available. Alternatives: 1) Find official Unity VFX Graph API, "
                "2) Use MenuItem/EditorUtility approach, 3) Template-based creation workflow.",
                '{"type": "technical_decision", "tags": ["vfx", "unity", "reflection", "api"], '
                '"priority": "high", "status": "in_development"}'
            ),
            (
                "Unity VFX Graph asset creation requires internal API access - no public API documented in Unity manual. "
                "This is a Unity limitation that may require community solutions or Unity support.",
                '{"type": "learning", "category": "unity_limitation", "topic": "vfx_graph"}'
            )
        ]

        for content, metadata in findings:
            cursor.execute(
                "INSERT INTO documents (content, metadata) VALUES (?, ?)",
                (content, metadata)
            )
            cursor.execute(
                "INSERT INTO documents_fts (content, metadata) VALUES (?, ?)",
                (content, metadata)
            )

        conn.commit()
        print(f"  [OK] Added {len(findings)} initial entries about VFX investigation")
        conn.close()

    except Exception as e:
        print(f"  [ERROR] Failed to add initial data: {e}")

print("\n" + "=" * 70)
if success:
    print("Database Initialization Complete!")
    print("\nDatabases created:")
    print(f"  - Public:  {public_db}")
    print(f"  - Private: {private_db}")
    print("\nYou can now:")
    print("  1. Search the KB using RAG engine")
    print("  2. Add notes with rag.quick_note()")
    print("  3. Log decisions with rag.log_decision()")
    print("  4. Track conversations with conversation_tracker")
else:
    print("Database initialization encountered errors. Check output above.")
    sys.exit(1)

print("=" * 70)
