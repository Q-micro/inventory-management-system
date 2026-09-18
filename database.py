import sqlite3
import os

DB_PATH = "sales.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sales.db")
conn = sqlite3.connect(DB_PATH)

conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER DEFAULT 1,
    item_condition TEXT,
    description TEXT,
    image_path TEXT,
    status TEXT DEFAULT 'available',
    date_added TEXT,
    date_sold TEXT
)
""")

# Add image_position column if it doesn't already exist
cursor.execute("PRAGMA table_info(items)")
columns = [column[1] for column in cursor.fetchall()]

if "image_position" not in columns:
    cursor.execute("""
        ALTER TABLE items
        ADD COLUMN image_position TEXT DEFAULT '50% 50%'
    """)

if "image_zoom" not in columns:
    cursor.execute("""
        ALTER TABLE items
        ADD COLUMN image_zoom REAL DEFAULT 1.0
    """)

conn.commit()
conn.close()

print("Database created/verified!")