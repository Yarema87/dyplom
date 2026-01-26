from flask import Blueprint, make_response, jsonify
from models.device import Device
from models.telemetry import Telemetry
from models.sensors import Sensor
from extensions import fernet

mod_simulator = Blueprint('simulator', __name__, url_prefix='/simulator')

@mod_simulator.route('/simulator/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    result = []
    for device in devices:
        result.append({
            'device_id': device.id,
            'connection_string': fernet.decrypt(device.connection_id).decode('utf-8'),
            'sensors': [{
                'id': sensor.id,
                'name': sensor.name,
                'unit': sensor.unit,
                'data_type': sensor.data_type,
                'min_value': sensor.min_value,
                'max_value': sensor.max_value
            } for sensor in device.sensors]
        })
    response = make_response(jsonify({'success': True, 'data': result}))
    return response, 200

@mod_simulator.route('/simulator/sensor/<int:sensor_id>', methods=['GET'])
def get_telemetry(sensor_id):
    telemetry = Telemetry.query.filter_by(sensor_id=sensor_id).order_by(Telemetry.timestamp.desc()).first()
    if not telemetry:
        response = make_response(jsonify({'success': False, 'error': 'telemetry not found'}))
        return response, 404
    response = make_response(jsonify({'success': True, 'telemetry': {'sensor_id': telemetry.sensor.id, 'value': telemetry.value, 'timestamp': telemetry.timestamp}}))
    return response, 200

@mod_simulator.route('/simulator/sensors', methods=['GET'])
def get_all_sensors():
    sensors = Sensor.query.all()
    result = []
    for sensor in sensors:
        result.append({
            'sensor_id': sensor.id,
            'min_value': sensor.min_value,
            'max_value': sensor.max_value,
            'device_id': sensor.device_id,
            'name': sensor.name,
            'data_type': sensor.data_type,
            'unit': sensor.unit
        })
    response = make_response(jsonify({'success': True, 'data': result}))
    return response, 200