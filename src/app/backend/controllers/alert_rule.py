from flask import Blueprint, request, make_response, jsonify, g
from models.alert_rule import AlertRule
from models.user import User
from extensions import db, redis_client
from user_check import admin_required, login_required
from redis_cache import cache_rule, delete_rule_cache

mod_rule = Blueprint('rule', __name__, url_prefix='/rule')

@mod_rule.route('/rule/add', methods=['POST'])
@login_required
@admin_required
def add_alert_rule():
    user_id = g.user.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    data = request.get_json()
    model = AlertRule()
    model.sensor_id = data.get('sensor_id') if data.get('sensor_id') != '' else None
    model.sensor_name = data.get('sensor_name') if data.get('sensor_name') != '' else None
    model.min_value = data.get('min_value') if data.get('min_value') != '' else None
    model.max_value = data.get('max_value') if data.get('max_value') != '' else None
    model.message = data.get('message')
    model.enabled = True
    model.organization = user.organization
    try:
        db.session.add(model)
        db.session.commit()
        cache_rule(model)
        response = make_response(jsonify({'success': True}))
        return response, 201
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': e}))
        return response, 500
    
@mod_rule.route('/rule/organization', methods=['GET'])
@login_required
@admin_required
def get_organization_rules():
    user_id = g.user.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    rules = AlertRule.query.filter_by(organization=user.organization).all()
    if not rules:
        response = make_response(jsonify({'success': False, 'error': 'None rules for this organization found'}))
        return response, 404
    rule_data = [{
        'id': rule.id,
        'sensor_id': rule.sensor_id,
        'sensor_name': rule.sensor_name,
        'min_value': rule.min_value,
        'max_value': rule.max_value,
        'message': rule.message,
        'enabled': rule.enabled
    } for rule in rules]
    response = make_response(jsonify({'success': True, 'rules': rule_data}))
    return response, 200

@mod_rule.route('/rule/remove/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    rule = AlertRule.query.filter_by(id=rule_id).first()
    if not rule:
        response = make_response(jsonify({'success': False, 'error': 'Rule not found'}))
        return response, 404
    try:
        db.session.delete(rule)
        db.session.commit()
        delete_rule_cache(rule_id)
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': str(e)}))
        return response, 500
    
@mod_rule.route('/rule/edit/<int:rule_id>', methods=['PATCH'])
def edit_rule(rule_id):
    rule = AlertRule.query.filter_by(id=rule_id).first()
    if not rule:
        response = make_response(jsonify({'success': False, 'error': 'Rule not found'}))
        return response, 404
    try:
        old_sensor_id = rule.sensor_id
        data = request.get_json()
        if data.get('type') == 'id':
            rule.sensor_id = data.get('sensor_id')
            rule.sensor_name = None
        elif data.get('type') == 'name':
            rule.sensor_id = None
            rule.sensor_name = data.get('sensor_name')
        rule.min_value = data.get('min_value') if data.get('min_value') != '' else None
        rule.max_value = data.get('max_value') if data.get('max_value') != '' else None
        rule.message = data.get('message')
        rule.enabled = data.get('enabled')
        db.session.commit()
        if rule.sensor_id != old_sensor_id:
            redis_client.srem(
                f'sensor:{old_sensor_id}:rules',
                rule.id
            )
        cache_rule(rule)
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': str(e)}))
        return response, 500
    

@mod_rule.route('/rule/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    rule = AlertRule.query.filter_by(id=rule_id).first()
    if not rule:
        response = make_response(jsonify({'success': False, 'error': 'Rule not found'}))
        return response, 404
    rule_data = {
        'id': rule.id,
        'sensor_id': rule.sensor_id,
        'sensor_name': rule.sensor_name,
        'min_value': rule.min_value,
        'max_value': rule.max_value,
        'message': rule.message,
        'enabled': rule.enabled
    }
    response = make_response(jsonify({'success': True, 'rule': rule_data}))
    return response, 200
    
