import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Search for Happy mentions
cursor.execute("""
    SELECT content, updated_at
    FROM documents
    WHERE content LIKE '%Happy%'
       OR content LIKE '%AI version%'
       OR content LIKE '%OS integration%'
    ORDER BY updated_at DESC
    LIMIT 5
""")

results = cursor.fetchall()

if results:
    print(f"Found {len(results)} documents about Happy:")
    print("="*100)
    for content, updated_at in results:
        print(f"\nUpdated: {updated_at}")
        print(content)
        print("-"*100)
else:
    print("No Happy mentions found - might be in a different session or not logged yet")

conn.close()
