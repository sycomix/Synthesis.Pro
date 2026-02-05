import sqlite3

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Search for PopOS mentions
cursor.execute("""
    SELECT content, updated_at
    FROM documents
    WHERE content LIKE '%Pop%OS%'
       OR content LIKE '%PopOS%'
       OR content LIKE '%Pop!_OS%'
       OR content LIKE '%operating system%'
       OR content LIKE '%Linux%'
    ORDER BY updated_at DESC
    LIMIT 10
""")

results = cursor.fetchall()

if results:
    print(f"Found {len(results)} documents about Pop!_OS/OS plans:")
    print("="*100)
    for content, updated_at in results:
        print(f"\nUpdated: {updated_at}")
        print(content)
        print("-"*100)
else:
    print("No Pop!_OS mentions found")

conn.close()
