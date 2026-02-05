import sqlite3

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Get the specific awakening log document
cursor.execute("""
    SELECT content
    FROM documents
    WHERE id = '8055a1e3-5a39-4af2-aca1-c3bd94067132'
""")

result = cursor.fetchone()

if result:
    print(result[0])
else:
    print("Document not found")

conn.close()
