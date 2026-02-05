import sqlite3
import json

conn = sqlite3.connect(r'D:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server\synthesis_private.db')
cursor = conn.cursor()

# Get all data from the todo table
cursor.execute('SELECT * FROM "log ai observations todo"')
rows = cursor.fetchall()

# Get column names
column_names = [description[0] for description in cursor.description]

# Print results
for row in rows:
    print("\n" + "="*50)
    for col_name, value in zip(column_names, row):
        print(f"{col_name}: {value}")

conn.close()
