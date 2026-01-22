import sqlite3

DB_PATH = './smarthome.db'

class Observer:
    def update(self, device_id, new_status):
        pass
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
        """Creates a connection to the SQLite database."""
        conn = sqlite3.connect(DB_PATH)
        # This allows us to access columns by name (row['name']) instead of index
        conn.row_factory = sqlite3.Row 
        return conn

    def init_db(self):
        """Creates the devices table if it doesn't exist."""
        conn = self.get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'off'
            )
        ''')
        conn.commit()
        conn.close()
    def __iter__(self):
        devices = self.get_all_devices()
        return DeviceIterator(devices)
    def add_device(self, name):
        """Adds a new device to the database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # SQL: Insert the new name. Status defaults to 'off'.
        cursor.execute('INSERT INTO devices (name) VALUES (?)', (name,))
        conn.commit()  # Save the change
        
        # Get the ID of the new item
        new_id = cursor.lastrowid
        
        # Retrieve the created device to return it
        device = conn.execute('SELECT * FROM devices WHERE id = ?', (new_id,)).fetchone()
        conn.close()
        return dict(device)

    def get_all_devices(self):
        """Returns the list of all devices."""
        conn = self.get_db_connection()
        devices = conn.execute('SELECT * FROM devices').fetchall()
        conn.close()
        # Convert database rows to a list of Python dictionaries
        return [dict(row) for row in devices]

    def get_device_by_id(self, device_id):
        """Finds a specific device by its ID."""
        conn = self.get_db_connection()
        device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
        conn.close()
        if device:
            return dict(device)
        return None
    def update_device_status(self, device_id, new_status):
        """Updates the status of a specific device."""
        conn = self.get_db_connection()
        
        # Check if device exists first
        device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
        if device is None:
            conn.close()
            return None

        # SQL: Update the status
        conn.execute('UPDATE devices SET status = ? WHERE id = ?', (new_status, device_id))
        conn.commit()
         # Notify observers about the status change
        self.notify_observers(device_id, new_status)
        # Fetch the updated device to return it
        updated_device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
        conn.close()
        return dict(updated_device)
    
    def delete_device(self, device_id):
        """Removes a device from the database."""
        conn = self.get_db_connection()
        
        # SQL: Delete the row
        cursor = conn.execute('DELETE FROM devices WHERE id = ?', (device_id,))
        conn.commit()
        
        # cursor.rowcount tells us how many rows were affected
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
class DeviceIterator:
    def __iter__(self):
        return self
    def __init__(self, devices):
        self.devices = devices
        self.index = 0
    def Current(self):
        return self.devices[self.index]
    def __next__(self):
        if self.isDone():
            raise StopIteration
        temp_device = self.Current()
        self.next()
        return temp_device
    def Current(self):
        return self.devices[self.index]
    def next(self):
        self.index += 1
    def isDone(self):
        if self.index >= len(self.devices):
            return True
        return False
    
class MobileApp(Observer):
    def update(self, device_id, new_status):
        print(f"Mobile App: Device {device_id} is now {new_status}")
if __name__ == "__main__":
    print("\n--- Final System Test ---")
    db = SmartHomeDB()
    
    # 1. Add some devices (if they aren't already there from previous runs)
    # Note: Since it's a real DB, you might have duplicates if you keep adding.
    # For this test, let's just update what we know exists.
    
    # 2. Create the App (Observer) and register it
    app = MobileApp()
    db.add_observer(app)
    
    # 3. Trigger an update!
    # Let's turn the "Kitchen Light" (assuming ID 1) to "ON"
    print("Updating device status...")
    db.update_device_status(1, "ON")
# class SmartHomeDB:
#     def __init__(self):
#         # This list acts as our "In-Memory Database"
#         # Data structure example: {"id": 1, "name": "Living Room Light", "status": "off"}
#         self.devices = []
#         self.id_counter = 1

#     def get_all_devices(self):
#         """Returns the list of all devices."""
#         return self.devices

#     def get_device_by_id(self, device_id):
#         """Finds a specific device by its ID."""
#         for device in self.devices:
#             if device["id"] == device_id:
#                 return device
#         return None

#     def add_device(self, name):
#         """Adds a new device to the database."""
#         new_device = {
#             "id": self.id_counter,
#             "name": name,
#             "status": "off" # Default status
#         }
#         self.devices.append(new_device)
#         self.id_counter += 1
#         return new_device
    
#     def update_device_status(self,device_id,new_status):
#         """Updates the status of a specific device."""
#         device = self.get_device_by_id(device_id)
#         if device:
#             device["status"] = new_status
#             return device
#         return None
#     def delete_device(self, device_id):
#         """Removes a device from the database."""
#         for i, device in enumerate(self.devices):
#             if device["id"] == device_id:
#                 del self.devices[i]
#                 return True # Successfully deleted
#         return False # Device not found
        