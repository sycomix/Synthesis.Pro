import sqlite3
import json

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Search for recent logs about Asset Store, beta, user experience, devlog
cursor.execute("""
    SELECT id, content, metadata, updated_at
    FROM documents
    WHERE content LIKE '%Asset Store%'
       OR content LIKE '%beta%'
       OR content LIKE '%user experience%'
       OR content LIKE '%devlog%'
       OR content LIKE '%submission%'
       OR content LIKE '%SP Test%'
       OR json_extract(metadata, '$.generated.title') LIKE '%asset%'
       OR json_extract(metadata, '$.generated.title') LIKE '%beta%'
    ORDER BY updated_at DESC
    LIMIT 15
""")

results = cursor.fetchall()

if results:
    print(f"Found {len(results)} documents about current work:")
    print("="*100)
    for doc_id, content, metadata, updated_at in results:
        try:
            meta_dict = json.loads(metadata) if metadata else {}
            title = meta_dict.get('generated', {}).get('title', 'No title')
        except:
            title = 'No title'

        print(f"\nUpdated: {updated_at}")
        print(f"Title: {title}")
        print(f"\nContent:")
        print(content)
        print("-"*100)
else:
    print("No current work documents found")

conn.close()
