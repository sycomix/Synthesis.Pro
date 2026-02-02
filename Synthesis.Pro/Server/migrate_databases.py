#!/usr/bin/env python3
"""
Database Migration Script
Migrates old Nightblade databases to new Synthesis.Pro dual-database architecture
"""

import sqlite3
import sys
import os
import argparse
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from RAG import SynthesisRAG


def inspect_database(db_path: str):
    """Inspect database structure and content"""
    print(f"\n{'='*60}")
    print(f"Inspecting: {db_path}")
    print(f"Size: {Path(db_path).stat().st_size / (1024*1024):.2f} MB")
    print(f"{'='*60}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\nTables: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} rows")

        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"    Columns: {', '.join([col[1] for col in columns])}")

        # Sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        samples = cursor.fetchall()
        if samples:
            print(f"    Sample rows:")
            for i, sample in enumerate(samples, 1):
                # Handle unicode safely - encode and decode to ASCII
                sample_str = str(sample)[:100].encode('ascii', 'replace').decode('ascii')
                print(f"      {i}. {sample_str}...")

    conn.close()
    return tables


def should_be_public(content: str, metadata: dict = None) -> bool:
    """
    Determine if content should go to public database

    Public criteria:
    - Unity API documentation
    - General C# patterns
    - Anonymous code examples
    - Asset Store integration guides
    - Open source Nightblade core features (sanitized)

    Private criteria:
    - Project-specific implementations
    - User preferences/notes
    - Custom business logic
    - Configuration details
    """

    # Keywords that suggest public knowledge
    public_indicators = [
        'Unity',
        'MonoBehaviour',
        'GameObject',
        'Transform',
        'Vector3',
        'Quaternion',
        'ScriptableObject',
        'Asset Store',
        'TextMeshPro',
        'UI Toolkit',
        'DOTS',
        'ECS',
        'Job System',
        'Burst',
        # Open source indicators
        'MIT License',
        'Apache License',
        'GPL',
        'open source',
    ]

    # Keywords that suggest private data
    private_indicators = [
        'API key',
        'password',
        'secret',
        'token',
        'credential',
        'private',
        'confidential',
        'TODO',
        'FIXME',
        'bug',
        'issue',
        # Project-specific
        'config',
        'settings',
        'preference',
    ]

    content_lower = content.lower()

    # Check for private indicators first (safety first)
    for indicator in private_indicators:
        if indicator.lower() in content_lower:
            return False

    # Check for public indicators
    for indicator in public_indicators:
        if indicator.lower() in content_lower:
            return True

    # Default to private for safety
    return False


def migrate_database(source_db: str, rag: SynthesisRAG, dry_run: bool = False):
    """
    Migrate content from old database to new dual-database system
    """
    print(f"\n{'='*60}")
    print(f"Migrating: {source_db}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}")

    conn = sqlite3.connect(source_db)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    stats = {
        'total': 0,
        'public': 0,
        'private': 0,
        'skipped': 0
    }

    for table in tables:
        table_name = table[0]
        print(f"\nProcessing table: {table_name}")

        # Skip metadata tables
        if table_name.startswith('sqlite_'):
            print(f"  Skipping system table")
            continue

        # Get all rows
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        for row in rows:
            stats['total'] += 1

            # Convert row to dict
            row_dict = dict(zip(columns, row))

            # Extract text content (look for common text columns)
            text_content = None
            for col in ['content', 'text', 'data', 'body', 'description']:
                if col in row_dict and row_dict[col]:
                    text_content = str(row_dict[col])
                    break

            if not text_content:
                # Try to concatenate all text fields
                text_content = ' '.join([str(v) for v in row_dict.values() if v])

            if not text_content or len(text_content.strip()) < 10:
                stats['skipped'] += 1
                continue

            # Determine if public or private
            is_public = should_be_public(text_content, row_dict)

            if is_public:
                stats['public'] += 1
                db_type = "PUBLIC"
            else:
                stats['private'] += 1
                db_type = "PRIVATE"

            # Show sample
            if stats['total'] <= 5:
                safe_sample = text_content[:100].encode('ascii', 'replace').decode('ascii')
                print(f"  [{db_type}] {safe_sample}...")

            # Add to appropriate database
            if not dry_run:
                success = rag.add_text(text_content, private=not is_public)
                if not success:
                    # Failure likely means duplicate content, skip it
                    stats['skipped'] += 1
                    # Don't count this in public/private stats
                    if is_public:
                        stats['public'] -= 1
                    else:
                        stats['private'] -= 1

    conn.close()

    print(f"\n{'='*60}")
    print(f"Migration Stats:")
    print(f"  Total rows: {stats['total']}")
    print(f"  -> Public: {stats['public']}")
    print(f"  -> Private: {stats['private']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"{'='*60}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Migrate Nightblade databases to Synthesis.Pro")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm migration (skip prompt)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")
    args = parser.parse_args()

    print("=" * 60)
    print("Synthesis.Pro Database Migration")
    print("=" * 60)

    # Paths
    old_db_dir = Path(__file__).parent.parent.parent / "Assets" / "Synthesis_AI" / "KnowledgeBase"
    nightblade_db = old_db_dir / "nightblade.db"
    nightblade_kb_db = old_db_dir / "nightblade_kb.db"

    # Target databases
    server_dir = Path(__file__).parent
    public_db = server_dir / "synthesis_knowledge.db"
    private_db = server_dir / "synthesis_private.db"

    # Check if source databases exist
    if not nightblade_db.exists() and not nightblade_kb_db.exists():
        print("ERROR: No source databases found!")
        print(f"   Looking for:")
        print(f"   - {nightblade_db}")
        print(f"   - {nightblade_kb_db}")
        return 1

    # Inspect databases first
    print("\nINSPECTION PHASE")
    print("=" * 60)

    if nightblade_db.exists():
        inspect_database(str(nightblade_db))

    if nightblade_kb_db.exists():
        inspect_database(str(nightblade_kb_db))

    # Ask for confirmation (unless --yes flag used)
    if args.yes:
        dry_run = args.dry_run
        print("\nAuto-confirmed: Proceeding with migration")
    else:
        print("\n" + "=" * 60)
        response = input("\nProceed with migration? (yes/dry-run/no): ").lower().strip()

        if response == 'no':
            print("Migration cancelled.")
            return 0

        dry_run = (response == 'dry-run')

    # Initialize RAG with dual databases
    print(f"\nInitializing Synthesis.Pro RAG Engine")
    print(f"   Public DB: {public_db}")
    print(f"   Private DB: {private_db}")

    rag = SynthesisRAG(
        database=str(public_db),
        private_database=str(private_db),
        embedding_provider="local"
    )

    # Migrate databases
    print("\nMIGRATION PHASE")

    total_stats = {
        'total': 0,
        'public': 0,
        'private': 0,
        'skipped': 0
    }

    if nightblade_kb_db.exists():
        stats = migrate_database(str(nightblade_kb_db), rag, dry_run)
        for key in total_stats:
            total_stats[key] += stats[key]

    if nightblade_db.exists():
        stats = migrate_database(str(nightblade_db), rag, dry_run)
        for key in total_stats:
            total_stats[key] += stats[key]

    # Final summary
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE" if not dry_run else "DRY RUN COMPLETE")
    print("=" * 60)
    print(f"Total rows processed: {total_stats['total']}")
    print(f"  -> Public database: {total_stats['public']} entries")
    print(f"  -> Private database: {total_stats['private']} entries")
    print(f"  Skipped: {total_stats['skipped']} entries")

    if not dry_run:
        print(f"\nNew databases created:")
        print(f"  PUBLIC: {public_db} ({public_db.stat().st_size / 1024:.1f} KB)")
        print(f"  PRIVATE: {private_db} ({private_db.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"\nRun without 'dry-run' to perform actual migration")

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
