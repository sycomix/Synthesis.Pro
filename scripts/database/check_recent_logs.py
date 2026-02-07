import sqlite3

db_path = 'd:/Unity Projects/Synthesis.Pro/Assets/Synthesis.Pro/Server/synthesis_private.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get total count
cursor.execute("SELECT COUNT(*) FROM documents")
total = cursor.fetchone()[0]
print(f"Total documents: {total}")

# Get most recent by ID
cursor.execute("SELECT id, content, added_at FROM documents ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

print("\n=== Most Recent Documents (by ID) ===")
for row in rows:
    doc_id, content, added_at = row
    preview = content[:120] if content else ''
    preview = preview.replace('\n', ' ')
    print(f"ID {doc_id}: {preview}...")
    print(f"        Added: {added_at}")
    print()

# Search for console logs specifically
cursor.execute("SELECT COUNT(*) FROM documents WHERE content LIKE '[CONSOLE:%'")
console_count = cursor.fetchone()[0]
print(f"Console log documents: {console_count}")

if console_count > 0:
    cursor.execute("SELECT id, content, added_at FROM documents WHERE content LIKE '[CONSOLE:%' ORDER BY id DESC LIMIT 5")
    print("\n=== Recent Console Logs ===")
    for row in cursor.fetchall():
        doc_id, content, added_at = row
        lines = content.split('\n')
        print(f"ID {doc_id} - {added_at}")
        for line in lines[:4]:  # First 4 lines
            print(f"  {line}")
        print()

conn.close()
