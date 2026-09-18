import sqlite3

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE items ADD COLUMN date_added TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE items ADD COLUMN date_sold TEXT")
except:
    pass

conn.commit()
conn.close()

print("Done")