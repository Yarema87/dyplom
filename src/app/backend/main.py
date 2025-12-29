from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from extensions import db
from user_check import load_user

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
from controllers.dashboard import mod_dashboard
from controllers.auth import mod_auth
from controllers.device import mod_device
from controllers.sensors import mod_sensor
from controllers.device_credentials import mod_credentials

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
app.register_blueprint(mod_dashboard, url_prefix='/api')
app.register_blueprint(mod_auth, url_prefix='/api')
app.register_blueprint(mod_device, url_prefix='/api')
app.register_blueprint(mod_sensor, url_prefix='/api')
app.register_blueprint(mod_credentials, url_prefix='/api')

app.before_request(load_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        port = int(os.getenv('PORT'))
        app.run(host='0.0.0.0', port=port, debug=False)