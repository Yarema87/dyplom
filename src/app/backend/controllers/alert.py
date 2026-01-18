from models.alert import Alert
from models.user import User
from models.device import Device
from models.alert_rule import AlertRule
from flask import Blueprint, g, make_response, jsonify
from user_check import login_required
from extensions import db

mod_alert = Blueprint('alert', __name__, url_prefix='/alert')

@mod_alert.route('/alert/user', methods=['GET'])
@login_required
def get_user_alerts():
    user_id = g.user.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    if user.access == 'admin':
        alerts = (
            db.session.query(Alert, AlertRule, Device, User).join(Device, Alert.device_id == Device.id).join(User, Device.user_id == User.id).join(AlertRule, Alert.rule_id == AlertRule.id).filter(User.organization == user.organization, Alert.resolved == False).all()
        )
        if not alerts:
            response = make_response(jsonify({'success': False, 'error': 'None alerts found for this organization'}))
            return response, 404
        alert_data = [{
            'id': alert.id,
            'rule_id': alert.rule_id,
            'device_id': alert.device_id,
            'sensor_id': alert.sensor_id,
            'value': alert.value,
            'triggered_at': alert.triggered_at,
            'resolved': alert.resolved,
            'message': alert_rule.message
        } for alert, alert_rule, device, user in alerts]
        response = make_response(jsonify({'success': True, 'alerts': alert_data}))
        return response, 200
    alerts = (
        db.session.query(Alert, AlertRule, Device, User).join(Device, Alert.device_id == Device.id).join(User, Device.user_id == User.id).filter(User.id == user_id, Alert.resolved == False).all()
    )
    if not alerts:
        response = make_response(jsonify({'success': False, 'error': 'None alerts found for this organization'}))
        return response, 404
    alert_data = [{
        'id': alert.id,
        'rule_id': alert.rule_id,
        'device_id': alert.device_id,
        'sensor_id': alert.sensor_id,
        'value': alert.value,
        'triggered_at': alert.triggered_at,
        'resolved': alert.resolved,
        'message': alert_rule.message
    } for alert, alert_rule, device, user in alerts]
    response = make_response(jsonify({'success': True, 'alerts': alert_data}))
    return response, 200

@mod_alert.route('/alert/resolve/<int:alert_id>', methods=['PATCH'])
def resolve_alert(alert_id):
    alert = Alert.query.filter_by(id=alert_id).first()
    if not alert:
        response = make_response(jsonify({'success': False, 'error': 'alert not found'}))
        return response, 404
    try:
        alert.resolved = True
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': str(e)}))
        return response, 500
    
@mod_alert.route('/alert/device/<int:device_id>', methods=['GET'])
def get_device_alerts(device_id):
    alerts = db.session.query(Alert, AlertRule, Device).join(Device, Alert.device_id == Device.id).join(AlertRule, Alert.rule_id == AlertRule.id).filter(Device.id == device_id).all()
    if not alerts:
        response = make_response(jsonify({'success': False, 'error': 'None alerts found for this device'}))
        return response, 404
    alert_data = [{
        'id': alert.id,
        'rule_id': alert.rule_id,
        'device_id': alert.device_id,
        'sensor_id': alert.sensor_id,
        'value': alert.value,
        'triggered_at': alert.triggered_at,
        'resolved': alert.resolved,
        'message': alert_rule.message
    } for alert, alert_rule, device in alerts]
    response = make_response(jsonify({'success': True, 'alerts': alert_data}))
    return response, 200
