import sqlite3

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in synthesis_private.db:")
print("="*50)
for table in tables:
    print(f"- {table[0]}")

    # Show row count for each table
    cursor.execute(f"SELECT COUNT(*) FROM \"{table[0]}\"")
    count = cursor.fetchone()[0]
    print(f"  Rows: {count}")
    print()

conn.close()
