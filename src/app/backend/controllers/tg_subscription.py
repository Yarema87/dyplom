from flask import Blueprint, request, make_response, jsonify
from models.tg_subscription import TgSubscription
from models.tg_token import TgToken
from datetime import datetime
from extensions import db

mod_subscription = Blueprint('subscription', __name__, url_prefix='/subscription')

@mod_subscription.route('/subscription/add', methods=['POST'])
def add_sub():
    data = request.get_json()
    token = data.get('token')
    token_data = TgToken.query.filter_by(token=token).first()
    if not token_data:
        response = make_response(jsonify({'success': False, 'error': 'token is invalid'}))
        return response, 400
    user_id = token_data.user_id
    chat_id = data.get('chat_id')
    enabled = True
    created_at = datetime.utcnow()
    try:
        existing = TgSubscription.query.filter_by(user_id=user_id, chat_id=chat_id).first()
        if existing:
            existing.enabled = True
            db.session.commit()
            response = make_response(jsonify({'success': True}))
            return response, 200
        model = TgSubscription()
        model.user_id = user_id
        model.chat_id = chat_id
        model.enabled = enabled
        model.created_at = created_at
        db.session.add(model)
        token_data.used = True
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 201
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': str(e)}))
        return response, 500
    
@mod_subscription.route('/subscription/get/<int:sub_id>', methods=['GET'])
def get_subscription(sub_id):
    subscription = TgSubscription.query.filter_by(chat_id=sub_id).first()
    if not subscription:
        response = make_response(jsonify({'success': False, 'error': 'Subscription not found'}))
        return response, 404
    response = make_response(jsonify({'success': True, 'subscription': subscription}))
    return response, 200

@mod_subscription.route('/subscription/disable/<int:sub_id>', methods=['PATCH'])
def disable_subscription(sub_id):
    subscription = TgSubscription.query.filter_by(chat_id=sub_id).first()
    if not subscription:
        response = make_response(jsonify({'success': False, 'error': 'Subscription not found'}))
        return response, 404
    try:
        subscription.enabled = False
        db.session.commit()
        response = make_response(jsonify({'success': True}))
        return response, 200
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': str(e)}))
        return response, 500
