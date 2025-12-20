from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from extensions import db

app = Flask(__name__)
CORS(app, 
     origins='http://localhost:3000',
     methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'content-type'],
     expose_headers=['Set-Cookie'],
     supports_credentials=True
)
load_dotenv()

from controllers.user import mod_user

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}
app.secret_key = os.getenv('SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(mod_user, url_prefix='/api')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        port = int(os.getenv('PORT'))
        app.run(host='0.0.0.0', port=port, debug=False)