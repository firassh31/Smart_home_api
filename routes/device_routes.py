# from flask import Blueprint, request, jsonify
# from database import SmartHomeDB

# device_bp = Blueprint('device_bp', __name__)
# db = SmartHomeDB()

# @device_bp.route('/', methods=['GET'])
# def get_devices():
#     data = db.get_all_devices()
#     return jsonify(data), 200

# @device_bp.route('/<int:device_id>', methods=['GET'])
# def get_single_device(device_id):
#     device = db.get_device_by_id(device_id)
#     if device:
#         return jsonify(device), 200 #OK
#     return jsonify({"error": "Device not found"}), 404 #Not found

# # Add a new device
# @device_bp.route('/', methods=['POST'])
# def create_device():
#     request_data = request.get_json()
#     # Basic validation
#     if not request_data or 'name' not in request_data:
#         return jsonify({"error": "Please provide a device name"}), 400
#     room = request_data.get('room', 'Living Room')
#     new_device = db.add_device(request_data['name'])
#     return jsonify(new_device), 201 #created

# @device_bp.route('/<int:device_id>', methods=['PUT'])
# def update_device(device_id):
#     request_data = request.get_json()
#     if not request_data or 'status' not in request_data:
#         return jsonify({"error":"missing 'status' field"}),400 #Bad request
#     new_status = request_data['status']
#     if new_status not in ['on', 'off']:
#         return jsonify({"error": "Invalid status. Use 'on' or 'off'"}), 400
#     updated_device = db.update_device_status(device_id, new_status)
#     if updated_device:
#         return jsonify(updated_device), 200
#     else:
#         return jsonify({"error": "Device not found"}), 404
    
# # Delete a device
# @device_bp.route('/<int:device_id>', methods=['DELETE'])
# def delete_device(device_id):
#     success = db.delete_device(device_id)
    
#     if success:
#         return jsonify({"message": "Device deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Device not found"}), 404

from flask import Blueprint, jsonify, request
from database import SmartHomeDB

device_bp = Blueprint('device_bp', __name__)
db = SmartHomeDB()

@device_bp.route('/', methods=['GET'])
def get_devices():
    return jsonify(db.get_all_devices())

@device_bp.route('/', methods=['POST'])
def add_device():
    data = request.get_json()
    name = data.get('name')
    room = data.get('room', 'Living Room')

    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    new_device = db.add_device(name, room)
    return jsonify(new_device), 201

@device_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    device_id = device_id.strip()
    print(f"DEBUG: Server received clean ID: '{device_id}'") # לוג מעודכן
    success = db.delete_device(device_id)
    if success:
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Device not found"}), 404

@device_bp.route('/<device_id>/status', methods=['PUT'])
def update_status(device_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['on', 'off']:
        return jsonify({"error": "Invalid status"}), 400

    updated_device = db.update_device_status(device_id, new_status)
    if updated_device:
        return jsonify(updated_device)
    return jsonify({"error": "Device not found"}), 404