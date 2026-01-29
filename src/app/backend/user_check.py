from flask import request, g, current_app, jsonify
import jwt
from functools import wraps

def load_user():
    token = request.cookies.get('auth_token')
    if not token:
        g.user = None
        return
    try:
        payload = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
        g.user = payload
    except jwt.ExpiredSignatureError:
        g.user = None
    except jwt.InvalidTokenError:
        g.user = None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user is None or g.user.get('approved') == False:
            return jsonify({'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user is None:
            return jsonify({'error': 'Unauthorized'}), 401
        if g.user.get('access') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        return fn(*args, **kwargs)
    return wrapper
