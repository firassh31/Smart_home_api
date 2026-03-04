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
    room = data.get('room')
    device_type = data.get('type')

    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    new_device = manager.add_device(name, room, device_type)
    return jsonify(new_device), 201

@device_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    device_id = device_id.strip()
    print(f"DEBUG: Server received clean ID: '{device_id}'")
    
    success = manager.delete_device(device_id)
    if success:
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Device not found"}), 404
# This route now calls the Manager, which handles the business logic and database interaction. The Manager will also take care of any Observer notifications if needed.
@device_bp.route('/<device_id>', methods=['PUT'])
def update_device_details(device_id):
    data = request.get_json()
    name = data.get('name')
    room = data.get('room')
    device_type = data.get('type')

    if not name or not room:
        return jsonify({"error": "Missing name or room"}), 400

    # Call our Manager to handle the update
    success = manager.update_device_details(device_id, name, room, device_type)
    
    if success:
        return jsonify({"message": "Device updated successfully"}), 200
    else:
        return jsonify({"error": "Device not found or update failed"}), 404
# This new route allows the frontend to update ON/OFF settings of a device without changing its name or room. The Manager will handle the logic of updating the database and notifying any observers about the change.
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
# This route allows the frontend to update specific settings of a device without changing its name or room. The Manager will handle the logic of updating the database and notifying any observers about the change.
@device_bp.route('/<device_id>/state', methods=['PUT'])
def update_device_state(device_id):
    state_updates = request.get_json()
    
    # Check if the frontend actually sent any data
    if not state_updates:
        return jsonify({"error": "No update data provided"}), 400
        
    updated_device = manager.update_device_state(device_id, state_updates)
    
    if updated_device:
        return jsonify(updated_device), 200
    return jsonify({"error": "Device not found or update failed"}), 404