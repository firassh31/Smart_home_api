import sqlite3
import patterns

DB_PATH = './smarthome.db'

class SmartHomeDB:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SmartHomeDB, cls).__new__(cls)
        return cls._instance
   
    def __init__(self):
        if SmartHomeDB._is_initialized is False:
            self.init_db()
            self.observers = []
            SmartHomeDB._is_initialized = True

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, device_id, new_status):
        for observer in self.observers:
            observer.update(device_id, new_status)

    def get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row 
        return conn

    def init_db(self):
        conn = self.get_db_connection()
        # Ensure table exists with the correct columns
        conn.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'off',
                room TEXT DEFAULT 'Living Room'
            )
        ''')
        # Simple migration: Try to add 'room' column if it was missing from an old DB
        try:
            conn.execute("ALTER TABLE devices ADD COLUMN room TEXT DEFAULT 'Living Room'")
        except sqlite3.OperationalError:
            pass # Column already exists
            
        conn.commit()
        conn.close()

    def get_all_devices(self):
        conn = self.get_db_connection()
        devices = conn.execute('SELECT * FROM devices').fetchall()
        conn.close()
        return [dict(row) for row in devices]

    def add_device(self, name, room):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO devices (name, status, room) VALUES (?, ?, ?)', (name, 'off', room))
        conn.commit()
        new_id = cursor.lastrowid
        device = conn.execute('SELECT * FROM devices WHERE id = ?', (new_id,)).fetchone()
        conn.close()
        return dict(device)

    def delete_device(self, device_id):
        conn = self.get_db_connection()
        cursor = conn.execute('DELETE FROM devices WHERE id = ?', (device_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def update_device_status(self, device_id, new_status):
        conn = self.get_db_connection()
        device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
        if device is None:
            conn.close()
            return None

        conn.execute('UPDATE devices SET status = ? WHERE id = ?', (new_status, device_id))
        conn.commit()
        self.notify_observers(device_id, new_status)
        updated_device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
        conn.close()
        return dict(updated_device)