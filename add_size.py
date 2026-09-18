import sqlite3

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE items
ADD COLUMN size TEXT
""")

conn.commit()
conn.close()

print("Size column added.")