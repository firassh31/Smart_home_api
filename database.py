import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import patterns

load_dotenv() 
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database("SmartHomeDB")

db.devices.create_index("room") # Creates an index on the "room" field to speed up queries that filter by room. This is especially useful as the number of devices grows.

class SmartHomeDB:
    _instance = None # This class variable will hold the single instance of SmartHomeDB that we create. It's initialized to None, and the first time we create an instance, we'll set it to that instance. Subsequent attempts to create an instance will return this same object, ensuring that all parts of our app are using the same database connection and observer list.
    _is_initialized = False # This flag is used to ensure that the init method only runs once. Since new can be called multiple times (if someone tries to create multiple instances), we want to make sure that the initialization code that sets up the observers list only runs the first time. After that, we set _is_initialized to True, and any subsequent calls to __init__ will skip the initialization code, preventing us from accidentally resetting our observers list or other state if someone tries to create another instance of SmartHomeDB.

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SmartHomeDB, cls).__new__(cls) #
        return cls._instance 
   
    def __init__(self):
        if SmartHomeDB._is_initialized is False:
            self.observers = []
            SmartHomeDB._is_initialized = True

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, device_id, new_status):
        for observer in self.observers:
            observer.update(device_id, new_status)

    def get_all_devices(self):
        try:
            # Fetch devices and let MongoDB sort them by 'room' (ascending), then 'name'
            # The '1' means ascending order (A-Z)
            cursor = db.devices.find().sort([("room", 1), ("name", 1)])
            
            devices = []
            for device in cursor:
                device['id'] = str(device['_id'])
                del device['_id']
                devices.append(device) # Convert the MongoDB cursor to a list of dictionaries, each representing a device. We also convert the '_id' field to a string and rename it to 'id' for easier use in the frontend.
            return devices # Return the sorted list of devices to the caller (e.g., the Flask route) so it can be sent to the frontend.
            
        except Exception as e:
            print(f"Database error while fetching devices: {e}")
            return [] # If there's an error (like a network issue), we return an empty list to avoid crashing the app. The frontend can handle this case by showing a message like "No devices found".
        
    def add_device(self, name, room):
        try:
            device = {
                "name": name,
                "room": room,
                "status": "off" 
            }
            result = db.devices.insert_one(device) #Inserts the new device document into the "devices" collection in MongoDB.
            device["id"] = str(result.inserted_id)
            del device['_id']
            return device # Return the newly created device with its ID for confirmation or further use in the app
            
        except Exception as e:
            # Catch network drops or database errors gracefully
            print(f"Database error while adding device: {e}")
            return None

    def delete_device(self, device_id):
        try:
            oid = ObjectId(device_id)  #Converts the string ID into a MongoDB ObjectId
        except:
            print("Invalid ID format")
            return False

        try:
            result = db.devices.delete_one({'_id': oid})  #Tells MongoDB to find and delete it directly on the server
            
            if result.deleted_count > 0:    #Checks if it was successfully deleted
                print(f"Successfully deleted device: {device_id}")
                return True
            else:
                print("No device found with that ID.")
                return False
                
        except Exception as e:
            print(f"Database error while trying to delete: {e}") # Catch any unexpected database or network crashes
            return False

    def update_device_status(self, device_id, new_status):
        try:
            oid = ObjectId(device_id) 
        except:
            return None # If the ID format is invalid, we return None to indicate failure without crashing the app.

        updated_device = db.devices.find_one_and_update(
            {'_id': oid},
            {'$set': {'status': new_status}},
            return_document=True
        )   #This method finds the device by its ID and updates its status in one atomic operation. It also returns the updated document so we can confirm the change and notify observers.

        if updated_device:
            updated_device['id'] = str(updated_device['_id'])
            del updated_device['_id']
            self.notify_observers(device_id, new_status)
            return updated_device
        return None # If the device wasn't found or there was an error, we return None to indicate failure.