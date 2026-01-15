import sqlite3
import os

DB_FILE = "rag_v2.db"

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Get current columns
    cursor.execute("PRAGMA table_info(source)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Current columns in 'source': {columns}")

    # Add extractedHierarchy if not exists
    if "extractedHierarchy" not in columns:
        print("Adding 'extractedHierarchy' column...")
        cursor.execute("ALTER TABLE source ADD COLUMN extractedHierarchy TEXT")
    else:
        print("'extractedHierarchy' column already exists.")

    # Add htmlContent if not exists
    if "htmlContent" not in columns:
        print("Adding 'htmlContent' column...")
        cursor.execute("ALTER TABLE source ADD COLUMN htmlContent TEXT")
    else:
        print("'htmlContent' column already exists.")
        
    # Check if extractedText exists and warn (SQLite cannot easily drop columns without creating a temp table)
    if "extractedText" in columns:
        print("Note: 'extractedText' column still exists. SQLite does not support simple DROP COLUMN in all versions. It stays but won't be used.")

    conn.commit()
    conn.close()
    print("Source Migration completed.")

    # Migrate Practice and Exam tables
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # --- PRACTICE ---
    cursor.execute("PRAGMA table_info(practice)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Current columns in 'practice': {columns}")

    if "title" not in columns:
        print("Adding 'title' column to practice...")
        # Adding as nullable first to avoid errors with existing data
        cursor.execute("ALTER TABLE practice ADD COLUMN title TEXT")
    
    if "description" not in columns:
        print("Adding 'description' column to practice...")
        cursor.execute("ALTER TABLE practice ADD COLUMN description TEXT")

    if "file" not in columns:
        print("Adding 'file' column to practice...")
        cursor.execute("ALTER TABLE practice ADD COLUMN file TEXT")

    # --- EXAM ---
    cursor.execute("PRAGMA table_info(exam)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Current columns in 'exam': {columns}")

    if "title" not in columns:
        print("Adding 'title' column to exam...")
        cursor.execute("ALTER TABLE exam ADD COLUMN title TEXT")
    
    if "description" not in columns:
        print("Adding 'description' column to exam...")
        cursor.execute("ALTER TABLE exam ADD COLUMN description TEXT")

    if "file" not in columns:
        print("Adding 'file' column to exam...")
        cursor.execute("ALTER TABLE exam ADD COLUMN file TEXT")

    if "status" not in columns:
        print("Adding 'status' column to exam...")
        cursor.execute("ALTER TABLE exam ADD COLUMN status TEXT DEFAULT 'Created'")

    conn.commit()
    conn.close()
    
    # Re-connect for Practice check (though we could reuse connection, sticking to pattern)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(practice)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Current columns in 'practice': {columns}")

    if "status" not in columns:
        print("Adding 'status' column to practice...")
        cursor.execute("ALTER TABLE practice ADD COLUMN status TEXT DEFAULT 'Created'")

    conn.commit()
    conn.close()
    print("Migration for Practice and Exam completed.")

    # --- QUESTION ---
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(question)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Current columns in 'question': {columns}")

    if "learnersAnswer" not in columns:
        print("Adding 'learnersAnswer' column to question...")
        cursor.execute("ALTER TABLE question ADD COLUMN learnersAnswer TEXT")
    else:
        print("'learnersAnswer' column already exists in question.")
    
    conn.commit()
    conn.close()
    print("Migration for Question completed.")

if __name__ == "__main__":
    migrate()
