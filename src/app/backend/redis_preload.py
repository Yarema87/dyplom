from redis_cache import cache_device, cache_sensor, cache_rule
from models.user import User
from models.alert import Alert
from models.device import Device
from models.telemetry import Telemetry
from models.sensors import Sensor
from models.alert_rule import AlertRule
from flask import Flask
from extensions import db, redis_client
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    db.init_app(app)

    return app

app = create_app()

def preload_redis():
    try:
        with app.app_context():
            print('Start caching')
            """for d in Device.query.all():
                cache_device(d)
            print('Devices cached')
            for s in Sensor.query.all():
                cache_sensor(s)
            print('Sensors cached')
            for r in AlertRule.query.all():
                cache_rule(r)
            print('Rules cached')"""
            rule_ids = set()
            rule_ids |= redis_client.smembers(f'sensor:1:rules')
            rule_ids |= redis_client.smembers(f'sensor:Temperature sensor:rules')
            rule_ids &= redis_client.smembers(f'org:LPNU:rules:enabled')
            for rule_id in rule_ids:
                rule = redis_client.hgetall(f'rule:{rule_id}')
                print(rule)
        print('All data successfully cached')
    except Exception as e:
        print('Error on caching data:', e)

if __name__ == '__main__':
    preload_redis()