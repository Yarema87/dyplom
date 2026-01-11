from flask import Blueprint, make_response, jsonify, request, g
from models.device import Device
from models.user import User
from datetime import datetime, timedelta
from extensions import db, fernet
from azure.iot.hub import IoTHubRegistryManager
import os
from user_check import login_required

mod_device = Blueprint('device', __name__, url_prefix='/device')

def device_status(last_seen):
    if not last_seen:
        return 'Not registered'
    delta = datetime.utcnow() - last_seen
    if delta <= timedelta(seconds=30):
        return 'Online'
    elif delta <= timedelta(minutes=3):
        return 'Delayed'
    else:
        return 'Offline'

@mod_device.route('/device/user/<int:user_id>', methods=['GET'])
def get_user_devices(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user.access == 'admin':
        operators = User.query.filter_by(organization=user.organization).all()
        devices = []
        for operator in operators:
            operator_devices = Device.query.filter_by(user_id=operator.id).all()
            for device in operator_devices:
                devices.append(device)
    else:
        devices = Device.query.filter_by(user_id=user_id).all()
    if not devices:
        response = make_response(jsonify({'success': False, 'message': 'User does not have any devices now'}))
        return response, 404
    devices_data = [
        {
            'id': device.id,
            'name': device.name,
            'description': device.description,
            'type': device.type,
            'latitude': device.latitude,
            'longitude': device.longitude,
            'user_id': device.user_id,
            'status': device_status(device.last_seen_at),
            'created_at': device.created_at,
            'last_seen_at': device.last_seen_at
        }
        for device in devices
    ]
    response = make_response(jsonify({'success': True, 'devices': devices_data}))
    return response, 200


@mod_device.route('/device/add', methods=['POST'])
@login_required
def add_device():
    data = request.get_json()

    formatted_time = datetime.utcnow()
    
    name = data.get('name')
    description = data.get('description')
    type = data.get('type')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    connection_id = data.get('connection')
    user_id = g.user['user_id']
    status = 'registered'
    created_at = formatted_time
    last_seen_at = formatted_time

    registry = IoTHubRegistryManager(os.getenv("AZURE_IOT_HUB_CONNECTION_STRING"))
    device = registry.get_device(connection_id)
    if not device:
        return jsonify({"error": "Device not found in IoT Hub"}), 404
    primary_key = device.authentication.symmetric_key.primary_key
    conn_str = f"HostName={os.getenv('HUB_NAME')};DeviceId={connection_id};SharedAccessKey={primary_key}"
    encrypted_connection = fernet.encrypt(conn_str.encode())

    model = Device()
    model.name = name
    model.description = description
    model.type = type
    model.latitude = latitude
    model.longitude = longitude
    model.connection_id = encrypted_connection
    model.user_id = user_id
    model.status = status
    model.created_at = created_at
    model.last_seen_at = last_seen_at
    try:
        db.session.add(model)
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 201
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': e}))
        return response, 400
    
@mod_device.route('/device/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.filter_by(id=device_id).first()
    if not device:
        response = make_response({'success': False, 'error': 'Device not found'})
        return response, 404
    device_data = {
            'id': device.id,
            'name': device.name,
            'description': device.description,
            'type': device.type,
            'latitude': device.latitude,
            'longitude': device.longitude,
            'user_id': device.user_id,
            'status': device_status(device.last_seen_at),
            'created_at': device.created_at,
            'last_seen_at': device.last_seen_at
        }
    response = make_response(jsonify({'success': True, 'device': device_data}))
    return response, 200

@mod_device.route('/device/remove/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.filter_by(id=device_id).first()
    if not device:
        response = make_response(jsonify({'success': False, 'error': 'device not found'}))
        return response, 404
    try:
        db.session.delete(device)
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': e}))
        return response, 400
