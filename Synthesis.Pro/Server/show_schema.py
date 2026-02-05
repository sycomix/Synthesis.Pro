import sqlite3

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Get schema for documents table
cursor.execute("PRAGMA table_info(documents)")
columns = cursor.fetchall()

print("Documents table schema:")
print("="*70)
for col in columns:
    print(f"{col[1]} ({col[2]})")

print("\n" + "="*70)
print("\nSample documents:")
cursor.execute("SELECT * FROM documents LIMIT 3")
docs = cursor.fetchall()

col_names = [description[0] for description in cursor.description]
print(f"Columns: {', '.join(col_names)}")

for i, doc in enumerate(docs, 1):
    print(f"\n--- Document {i} ---")
    for col_name, value in zip(col_names, doc):
        if isinstance(value, str) and len(value) > 200:
            print(f"{col_name}: {value[:200]}...")
        else:
            print(f"{col_name}: {value}")

conn.close()
