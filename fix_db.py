import sqlite3
import os

db_path = "rag_v2.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE practice ADD COLUMN created_at DATETIME")
        conn.commit()
        print("Successfully added created_at column to practice table.")
    except sqlite3.OperationalError as e:
        print(f"Error or already exists: {e}")
    finally:
        conn.close()
else:
    print(f"Database file {db_path} not found.")
