from flask import Blueprint, jsonify, request
from helper import DeviceManager  # Import the Manager instead of the DB

device_bp = Blueprint('device_bp', __name__)
manager = DeviceManager()  # Instantiate the Manager

@device_bp.route('/', methods=['GET'])
def get_devices():
    return jsonify(manager.get_all_devices())

@device_bp.route('/', methods=['POST'])
def add_device():
    data = request.get_json()
    name = data.get('name')
    room = data.get('room', 'Living Room')

    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    new_device = manager.add_device(name, room)
    return jsonify(new_device), 201

@device_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    device_id = device_id.strip()
    print(f"DEBUG: Server received clean ID: '{device_id}'")
    
    success = manager.delete_device(device_id)
    if success:
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Device not found"}), 404

@device_bp.route('/<device_id>/status', methods=['PUT'])
def update_status(device_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['on', 'off']:
        return jsonify({"error": "Invalid status"}), 400

    # This now calls the Manager, which updates the DB AND notifies Observers!
    updated_device = manager.update_device_status(device_id, new_status)
    if updated_device:
        return jsonify(updated_device)
    return jsonify({"error": "Device not found"}), 404