from azure.eventhub import EventHubConsumerClient
from extensions import db
from models.user import User
from models.device import Device
from models.sensors import Sensor
from models.telemetry import Telemetry
from models.alert_rule import AlertRule
from models.alert import Alert
from dotenv import load_dotenv
import os
from flask import Flask
from sqlalchemy import or_
from datetime import datetime

load_dotenv()

CONNSECTION_STRING = os.getenv('EVENT_HUB_CONNECTION_STRING')
EVENT_HUB_NAME = os.getenv('EVENT_HUB_NAME')
CONSUMER_GROUP = '$Default'

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return app

app = create_app()

def check_rule(rule, value):
    if rule.min_value is not None and value < rule.min_value:
        return True
    if rule.max_value is not None and value > rule.max_value:
        return True
    return False

def alert_cooldown(rule_id, sensor_id):
    COOLDOWN_SECONDS = 300
    last_event = Alert.query.filter(
        Alert.rule_id == rule_id,
        Alert.sensor_id == sensor_id,
        Alert.resolved == False
    ).order_by(Alert.triggered_at.desc()).first()
    if last_event:
        delta = (datetime.utcnow() - last_event.triggered_at).total_seconds()
        return delta >= COOLDOWN_SECONDS
    return True

def on_event(partition_context, event):
    payload = event.body_as_json()

    with app.app_context():
        try:
            model = Telemetry()
            sensor_id = payload['sensor']
            timestamp = payload['timestamp']
            sensor = Sensor.query.filter_by(id=sensor_id).first()
            sensor_name = sensor.name
            device = Device.query.filter_by(id=payload['device_id']).first()
            device.last_seen_at = datetime.fromisoformat(timestamp)
            user = User.query.filter_by(id=device.user_id).first()
            rules = AlertRule.query.filter(
                AlertRule.enabled == True,
                AlertRule.organization == user.organization,
                or_(
                    AlertRule.sensor_id == sensor_id,
                    AlertRule.sensor_name == sensor_name
                )
            ).all()
            value = payload['value']
            model.sensor_id = sensor_id
            model.value = value
            model.timestamp = timestamp
            db.session.add(model)
            db.session.flush()
            for rule in rules:
                if check_rule(rule, value):
                    if alert_cooldown(rule.id, sensor_id):
                        alert = Alert()
                        alert.rule_id = rule.id
                        alert.sensor_id = sensor_id
                        alert.device_id = device.id
                        alert.value = value
                        alert.triggered_at = datetime.utcnow()
                        alert.resolved = False
                        db.session.add(alert)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('db error:', e)
        finally:
            db.session.remove()

    partition_context.update_checkpoint(event)

client = EventHubConsumerClient.from_connection_string(
    conn_str=CONNSECTION_STRING,
    consumer_group=CONSUMER_GROUP,
    eventhub_name=EVENT_HUB_NAME,
)

with client:
    client.receive(
        on_event=on_event,
        starting_position='@latest',
    )