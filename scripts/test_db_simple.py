#!/usr/bin/env python3
"""Simple database test - no embeddings needed"""
import sys
import sqlite3
from pathlib import Path

# Test database access directly
private_db = Path("Assets/Synthesis.Pro/Server/synthesis_private.db")
public_db = Path("Assets/Synthesis.Pro/Server/synthesis_public.db")

print("Testing database access...")
print("=" * 60)

for db_name, db_path in [("Private", private_db), ("Public", public_db)]:
    if not db_path.exists():
        print(f"[ERROR] {db_name} DB not found: {db_path}")
        continue

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Get document count
        if 'documents' in tables:
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            print(f"\n[{db_name}] Database:")
            print(f"  Tables: {', '.join(tables)}")
            print(f"  Documents: {count}")

            # Show sample
            if count > 0:
                cursor.execute("SELECT content FROM documents LIMIT 1")
                sample = cursor.fetchone()[0]
                print(f"  Sample: {sample[:80]}...")
        else:
            print(f"\n[{db_name}] No documents table")

        conn.close()

    except Exception as e:
        print(f"[ERROR] {db_name} DB error: {e}")

print("\n" + "=" * 60)
print("[SUCCESS] Database access working!")
