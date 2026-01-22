from flask import Blueprint, g, make_response, jsonify
from user_check import admin_required, login_required
from models.user import User
from models.device import Device
from models.sensors import Sensor
from controllers.device import device_status
from extensions import db

mod_admin = Blueprint('admin', __name__, url_prefix='/admin')

@mod_admin.route('/admin/operators', methods=['GET'])
@login_required
@admin_required
def get_admin_operators():
    admin_id = g.user.get('user_id')
    admin = User.query.filter_by(id=admin_id).first()
    operators = User.query.filter_by(organization=admin.organization).all()
    if not operators:
        response = make_response(jsonify({'success': False, 'error': 'None operators of this organisation are found'}))
        return response, 404
    operators_data = [{
        'id': operator.id,
        'name': operator.name,
        'email': operator.email,
        'status': operator.approved
    } for operator in operators]
    response = make_response(jsonify({'success': True, 'operators': operators_data}))
    return response, 200

@mod_admin.route('/admin/devices', methods=['GET'])
@login_required
@admin_required
def get_admin_devices():
    admin_id = g.user.get('user_id')
    admin = User.query.filter_by(id=admin_id).first()
    devices = Device.query.join(User, Device.user_id == User.id).filter(User.organization == admin.organization).all()
    if not devices:
        response = make_response(jsonify({'success': False, 'error': 'None devices found for this organization'}))
        return response, 404
    device_data = [{
        'id': device.id,
        'name': device.name,
        'type': device.type,
        'latitude': device.latitude,
        'longitude': device.longitude,
        'status': device_status(device.last_seen_at),
        'last_seen_at': device.last_seen_at,
        'user_id': device.user_id
    } for device in devices]
    response = make_response(jsonify({'success': True, 'devices': device_data}))
    return response, 200

@mod_admin.route('/admin/sensors', methods=['GET'])
@login_required
@admin_required
def get_admin_sensors():
    admin_id = g.user.get('user_id')
    admin = User.query.filter_by(id=admin_id).first()
    sensors = Sensor.query.join(Device, Sensor.device_id == Device.id).join(User, Device.user_id == User.id).filter(User.organization == admin.organization).all()
    if not sensors:
        response = make_response(jsonify({'success': False, 'error': 'None sensors found for this organization'}))
        return response, 404
    sensor_names = set()
    for sensor in sensors:
        sensor_names.add(sensor.name)
    names_list = [{
        'name': name
    } for name in sensor_names]
    sensor_data = [{
        'id': sensor.id,
        'name': sensor.name,
        'data_type': sensor.data_type,
        'unit': sensor.unit,
        'max_value': sensor.max_value,
        'min_value': sensor.min_value,
        'device_id': sensor.device_id
    } for sensor in sensors]
    response = make_response(jsonify({'success': True, 'sensors': sensor_data, 'names': names_list}))
    return response, 200

@mod_admin.route('/admin/approve/<int:user_id>', methods=['PATCH'])
def approve_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        response = make_response(jsonify({'success': False, 'error': 'User not found'}))
        return response, 404
    try:
        user.approved = True
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': e}))
        return response, 500
    
@mod_admin.route('/admin/dismiss/<int:user_id>', methods=['PATCH'])
def dismiss_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        response = make_response(jsonify({'success': False, 'error': 'User not found'}))
        return response, 404
    try:
        user.approved = False
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': e}))
        return response, 500
