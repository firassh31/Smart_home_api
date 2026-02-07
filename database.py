import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import patterns

load_dotenv() 
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database("SmartHomeDB")

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
            self.observers = []
            SmartHomeDB._is_initialized = True

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, device_id, new_status):
        for observer in self.observers:
            observer.update(device_id, new_status)

    

    def get_all_devices(self):
        
        cursor = db.devices.find()
        
        devices = []
        for device in cursor:
            device['id'] = str(device['_id'])
            del device['_id']
            devices.append(device)
            
        return devices

    def add_device(self, name, room):
        device = {
            "name": name,
            "room": room,
            "status": "off" 
        }
        result = db.devices.insert_one(device)
        device["id"] = str(result.inserted_id)
        del device['_id']
        return device

    def delete_device(self, device_id):
        try:
            oid = ObjectId(device_id)
            print(f"Converted to ObjectId: {oid}")
        except:
            print("Could not convert to ObjectId")
            return False

        print("Scanning DB for matches...")
        all_devices = db.devices.find()
        found_any = False
        for d in all_devices:
            db_id = d['_id']
            print(f"Found doc with ID: {db_id} (Type: {type(db_id)})")
            
            if db_id == oid:
                print(">>> MATCH FOUND with ObjectId! <<<")
                found_any = True
            elif str(db_id) == device_id:
                 print(">>> MATCH FOUND but it is a STRING (not ObjectId)! <<<")

        if not found_any:
            print("No exact match found scanning the DB.")
        result = db.devices.delete_one({'_id': oid})
        return result.deleted_count > 0

    def update_device_status(self, device_id, new_status):
        try:
            oid = ObjectId(device_id)
        except:
            return None

        updated_device = db.devices.find_one_and_update(
            {'_id': oid},
            {'$set': {'status': new_status}},
            return_document=True
        )

        if updated_device:
            updated_device['id'] = str(updated_device['_id'])
            del updated_device['_id']
            self.notify_observers(device_id, new_status)
            return updated_device
        return None