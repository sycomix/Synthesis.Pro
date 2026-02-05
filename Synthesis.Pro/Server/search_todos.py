import sqlite3

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Search for documents containing "todo" or "task" or "observation"
cursor.execute("""
    SELECT id, path, content
    FROM documents
    WHERE content LIKE '%todo%'
       OR content LIKE '%TODO%'
       OR content LIKE '%task%'
       OR content LIKE '%observation%'
       OR path LIKE '%todo%'
       OR path LIKE '%task%'
    LIMIT 20
""")

results = cursor.fetchall()

if results:
    print("Found documents with todo/task/observation content:")
    print("="*70)
    for doc_id, path, content in results:
        print(f"\nDocument ID: {doc_id}")
        print(f"Path: {path}")
        print(f"Content (first 500 chars):")
        print(content[:500] if content else "No content")
        print("-"*70)
else:
    print("No documents found with todo/task content")
    print("\nLet me show you all documents instead:")
    cursor.execute("SELECT id, path, substr(content, 1, 100) FROM documents LIMIT 10")
    all_docs = cursor.fetchall()
    for doc_id, path, preview in all_docs:
        print(f"\n{doc_id}: {path}")
        print(f"   Preview: {preview}")

conn.close()
