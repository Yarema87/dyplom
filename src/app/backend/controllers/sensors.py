from flask import Blueprint, make_response, jsonify, request
from models.sensors import Sensor
from extensions import db

mod_sensor = Blueprint('sensors', __name__, url_prefix='/sensors')

@mod_sensor.route('/sensors/device/<int:device_id>', methods=['GET'])
def get_sensors(device_id):
    sensors = Sensor.query.filter_by(device_id=device_id).all()
    if not sensors:
        response = make_response(jsonify({'success': False, 'message': 'This device does not have any sensors'}))
        return response, 404
    sensor_data = [{
        'id': sensor.id,
        'name': sensor.name,
        'unit': sensor.unit,
        'data_type': sensor.data_type,
        'min_value': sensor.min_value,
        'max_value': sensor.max_value
    } for sensor in sensors]
    response = make_response(jsonify({'success': True, 'sensors': sensor_data}))
    return response, 200

@mod_sensor.route('sensors/add', methods=['POST'])
def add_sensor():
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    data_type = data.get('data_type')
    min_value = data.get('min_value')
    max_value = data.get('max_value')
    device_id = data.get('device_id')

    model = Sensor()
    model.name = name
    model.unit = unit
    model.data_type = data_type
    model.min_value = min_value
    model.max_value = max_value
    model.device_id = device_id

    try:
        db.session.add(model)
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 201
    except Exception as e:
        db.session.rollback
        response = make_response(jsonify({'success': False, 'error': e}))
        return response, 400