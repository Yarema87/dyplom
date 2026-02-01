from extensions import db, bot
from flask import Blueprint, request, make_response, jsonify, current_app, url_for, redirect
from models.user import User
from models.tg_subscription import TgSubscription
import bcrypt
import datetime
import jwt
from oauth_config import oauth
import os
from dotenv import load_dotenv
import requests

load_dotenv()
mod_user = Blueprint('user', __name__, url_prefix='/user')

@mod_user.route('/user/sign-up', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    organization = data.get('organization')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({
            'success': False,
            'message': 'User already registered'
        }), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        model = User()
        model.name = name
        model.email = email
        model.organization = organization
        model.password = hashed_password.decode('utf-8')
        model.access = 'user'
        model.approved = False

        db.session.add(model)
        db.session.commit()
        registration_notification(model)
        print('Notification system called')
        response = make_response(jsonify({'success': True}))
        return response, 201
    except Exception as e:
        response = make_response(jsonify({'success': False, 'message': f"Error on registering user: {e}"}))
        return response, 500
    

@mod_user.route('/user/login', methods=['POST'])
def log_in():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)
    user = User.query.filter_by(email=email).first()
    if not user:
        response = make_response(jsonify({'success': False, 'error': 'User not registered'}))
        return response, 404
    if not user.approved:
        response = make_response(jsonify({'success': False, 'error': 'User not approved'}))
        return response, 403
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        if not remember:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'access': user.access,
                'approved': user.approved,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
        else:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'access': user.access,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
            }
        token = jwt.encode(payload, current_app.secret_key, algorithm='HS256')

        response = make_response(jsonify({'success': True}))
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            samesite='None',
            secure=True,
            max_age=30*24*60*60 if remember else 24*60*60
        )
        return response, 200
    response = make_response(jsonify({'success': False, 'message': 'Wrong email or password'}))
    return response, 401

@mod_user.route('/user/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'success': True, 'message': 'Logged out successfully'}))
    response.set_cookie(
        'auth_token', 
        '', 
        httponly=True,
        samesite='None',
        secure=True,
        expires=0
    )
    return response, 200

def registration_notification(user):
    print('Notification system answered')
    admin = User.query.filter_by(organization=user.organization, access='admin').first()
    if not admin:
        response = {'success': True, 'error': 'There are no admin of this organization'}
        user.approved = True
        db.session.commit()
        return response
    print('Admin found')
    subscription = TgSubscription.query.filter_by(user_id=admin.id).first()
    if not subscription:
        response = {'success': False, 'error': 'Admin will not be notified'}
        return response
    chat_id = subscription.chat_id
    print('Subscription found')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    text = (
        f'New registration!\n\n'
        f'User - {user.name}\n'
        f'Email - {user.email}\n\n'
        f'Approve or dismiss him in app'
    )
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ Approve",
                    "callback_data": f"approve:{user.id}"
                },
                {
                    "text": "⏳ Not now",
                    "callback_data": f"later:{user.id}"
                }
            ]
        ]
    }
    print('Payload formed')
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        json={
            'chat_id': chat_id,
            'text': text,
            'reply_markup': reply_markup
        },
        timeout=5
    )
    print('Alert sent')

@mod_user.route('/user/google/callback', methods=['GET'])
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token, nonce=None)
    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        response = make_response(jsonify({'success': False, 'error': 'User not registered'}))
        return response, 404
    if not user.approved:
        response = make_response(jsonify({'success': False, 'error': 'User not approved'}))
        return response, 403
    payload = {
        'user_id': user.id,
        'email': user.email,
        'access': user.access,
        'approved': user.approved,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, current_app.secret_key, algorithm='HS256')
    response = redirect('http://localhost:3000/')
    response.set_cookie(
        'auth_token',
        token,
        httponly=True,
        samesite='None',
        secure=True,
        max_age=24*60*60
    )
    return response

@mod_user.route('/user/google/login', methods=['GET'])
def google_login():
    redirect_uri = url_for('user.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)