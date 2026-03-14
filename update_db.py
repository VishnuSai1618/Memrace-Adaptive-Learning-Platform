import sqlite3

db_path = 'instance/flashcard_system.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add columns one by one as SQLite doesn't support multiple ADD COLUMN in one statement
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
        print("Added xp column")
    except sqlite3.OperationalError as e:
        print(f"xp column: {e}")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1")
        print("Added level column")
    except sqlite3.OperationalError as e:
        print(f"level column: {e}")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0")
        print("Added streak column")
    except sqlite3.OperationalError as e:
        print(f"streak column: {e}")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_study_date DATE")
        print("Added last_study_date column")
    except sqlite3.OperationalError as e:
        print(f"last_study_date column: {e}")
        
    conn.commit()
    print("Database update complete!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
