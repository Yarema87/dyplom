from extensions import db
from flask import Blueprint, request, make_response, jsonify, current_app
from models.user import User
import bcrypt
import datetime
import jwt

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
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        if not remember:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'access': user.access,
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
            max_age=30*24*60*60 if remember else 24*60*60
        )
        return response, 200
    response = make_response(jsonify({'success': False, 'message': 'Wrong email or password'}))
    return response, 401