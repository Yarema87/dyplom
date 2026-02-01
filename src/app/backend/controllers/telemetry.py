from flask import Blueprint, make_response, jsonify
from models.telemetry import Telemetry
from datetime import datetime, timedelta

mod_telemetry = Blueprint('telemetry', __name__, url_prefix='/telemetry')

@mod_telemetry.route('/telemetry/<int:sensor_id>/<int:days>', methods=['GET'])
def get_telemetry(sensor_id, days):
    time = (datetime.utcnow() - timedelta(days=days)).isoformat()
    telemetry = Telemetry.query.filter(Telemetry.sensor_id == sensor_id, Telemetry.timestamp >= time).order_by(Telemetry.timestamp.asc()).all()
    if not telemetry:
        response = make_response(jsonify({'success': False, 'error': 'telemetry not found'}))
        return response, 404
    result = [
        {
            'timestamp': t.timestamp,
            'value': t.value
        }
        for t in telemetry
    ]
    response = make_response(jsonify({'success': True, 'telemetry': result}))
    return response, 200

@mod_telemetry.route('/telemetry/<int:sensor_id>/latest', methods=['GET'])
def get_latest(sensor_id):
    latest = Telemetry.query.filter_by(sensor_id=sensor_id).order_by(Telemetry.timestamp.desc()).first()
    if not latest:
        response = make_response(jsonify({'success': False, 'error': 'telemetry not found'}))
        return response, 404
    result = {
            'timestamp': latest.timestamp,
            'value': latest.value
        }
        
    response = make_response(jsonify({'success': True, 'telemetry': result}))
    return response, 200