import sqlite3
import json

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Search for documents with todo-related content
cursor.execute("""
    SELECT id, uri, content, metadata
    FROM documents
    WHERE content LIKE '%todo%'
       OR content LIKE '%TODO%'
       OR content LIKE '%Task%'
       OR content LIKE '%observation%'
       OR json_extract(metadata, '$.generated.title') LIKE '%todo%'
       OR json_extract(metadata, '$.generated.title') LIKE '%task%'
    ORDER BY updated_at DESC
    LIMIT 10
""")

results = cursor.fetchall()

if results:
    print(f"Found {len(results)} todo-related documents:")
    print("="*100)
    for doc_id, uri, content, metadata in results:
        try:
            meta_dict = json.loads(metadata) if metadata else {}
            title = meta_dict.get('generated', {}).get('title', 'No title')
        except:
            title = 'No title'

        print(f"\nTitle: {title}")
        print(f"ID: {doc_id}")
        print(f"URI: {uri if uri else 'None'}")
        print(f"\nContent:")
        print(content if len(content) < 2000 else content[:2000] + "... (truncated)")
        print("-"*100)
else:
    print("No todo-related documents found. Let me show recent documents:")
    cursor.execute("SELECT id, content, metadata FROM documents ORDER BY updated_at DESC LIMIT 5")
    recent = cursor.fetchall()
    for doc_id, content, metadata in recent:
        print(f"\n{doc_id}: {content[:150]}...")

conn.close()
