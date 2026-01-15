import sqlite3
import os
from datetime import datetime

db_path = "rag_v2.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(f"UPDATE practice SET created_at = ? WHERE created_at IS NULL", (now,))
        conn.commit()
        print(f"Updated existing practice rows with default timestamp: {now}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"Database file {db_path} not found.")
