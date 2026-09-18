import sqlite3

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

columns_to_add = [
    ("quantity", "INTEGER DEFAULT 1"),
    ("image_path", "TEXT"),
    ("date_added", "TEXT"),
    ("date_sold", "TEXT")
]

for column_name, column_type in columns_to_add:
    try:
        cursor.execute(
            f"ALTER TABLE items ADD COLUMN {column_name} {column_type}"
        )
        print(f"Added: {column_name}")
    except sqlite3.OperationalError:
        print(f"Already exists: {column_name}")

conn.commit()
conn.close()

print("Database upgraded!")