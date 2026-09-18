import sqlite3

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE items
        ADD COLUMN instagram_posted INTEGER DEFAULT 0
    """)

    print("Instagram column added!")

except Exception as e:
    print("Already exists:", e)

conn.commit()
conn.close()