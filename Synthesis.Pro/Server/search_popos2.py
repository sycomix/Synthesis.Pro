import sqlite3
import sys

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Search for PopOS mentions
cursor.execute("""
    SELECT content, updated_at
    FROM documents
    WHERE content LIKE '%Pop%OS%'
       OR content LIKE '%PopOS%'
       OR content LIKE '%Pop!_OS%'
       OR content LIKE '%custom OS%'
       OR content LIKE '%bet%'
    ORDER BY updated_at DESC
    LIMIT 5
""")

results = cursor.fetchall()

if results:
    print(f"Found {len(results)} documents:")
    print("="*100)
    for content, updated_at in results:
        print(f"\nUpdated: {updated_at}")
        print(content[:1000] if len(content) > 1000 else content)
        print("-"*100)
else:
    print("No matches found")

conn.close()
