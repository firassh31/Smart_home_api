from patterns import Observer
from database import SmartHomeDB


# Client code

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