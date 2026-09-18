import sqlite3

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE items
ADD COLUMN image_path TEXT
""")

conn.commit()
conn.close()

print("Image column added!")