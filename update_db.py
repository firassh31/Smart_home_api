import sqlite3

DB_PATH = './smarthome.db'

def add_room_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # This SQL command adds the new column
        cursor.execute("ALTER TABLE devices ADD COLUMN room TEXT DEFAULT 'Living Room'")
        conn.commit()
        print("✅ Success! Added 'room' column to database.")
    except sqlite3.OperationalError:
        print("⚠️  Column 'room' already exists. No changes made.")
    
    conn.close()

if __name__ == "__main__":
    add_room_column()