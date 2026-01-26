from flask import Blueprint, g, make_response, jsonify
from models.tg_token import TgToken
from user_check import login_required
import secrets
from datetime import datetime, timedelta
from extensions import db
import os
from dotenv import load_dotenv

mod_token = Blueprint('token', __name__, url_prefix='/token')
load_dotenv()

@mod_token.route('/token/add', methods=['POST'])
@login_required
def add_token():
    BOT_USERNAME = os.getenv('BOT_USERNAME')
    user_id = g.user.get('user_id')
    token = secrets.token_urlsafe(32)
    try:
        model = TgToken()
        model.token = token
        model.user_id = user_id
        model.expires_at = datetime.utcnow() + timedelta(minutes=10)
        model.used = False
        db.session.add(model)
        db.session.commit()

        link = f'https://t.me/{BOT_USERNAME}?start={token}'
        response = make_response(jsonify({'success': True, 'link': link}))
        return response, 201
    except Exception as e:
        db.session.rollback()
        response = make_response(jsonify({'success': False, 'error': str(e)}))
        return response, 500
    