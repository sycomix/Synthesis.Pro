import sqlite3
import json
from datetime import datetime

db_path = 'd:/Unity Projects/Synthesis.Pro/Assets/Synthesis.Pro/Server/synthesis_private.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get schema
cursor.execute("PRAGMA table_info(documents)")
columns = cursor.fetchall()
print("=== Documents Table Schema ===")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Get total count
cursor.execute("SELECT COUNT(*) FROM documents")
total = cursor.fetchone()[0]
print(f"\n=== Total Documents: {total} ===")

# Get recent documents
cursor.execute("SELECT * FROM documents ORDER BY added_at DESC LIMIT 5")
rows = cursor.fetchall()

if rows:
    print("\n=== Recent Documents ===")
    col_names = [desc[0] for desc in cursor.description]
    for row in rows:
        print(f"\n--- Document ---")
        for i, col_name in enumerate(col_names):
            value = row[i]
            if col_name == 'added_at':
                try:
                    dt = datetime.fromisoformat(value) if value else None
                    if dt:
                        value = f"{value} ({dt.strftime('%Y-%m-%d %H:%M:%S')})"
                except:
                    pass
            elif col_name == 'content' and len(str(value)) > 200:
                value = str(value)[:200] + '...'
            elif col_name == 'metadata':
                try:
                    value = json.loads(value) if value else None
                except:
                    pass
            print(f"  {col_name}: {value}")

conn.close()
