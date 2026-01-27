from azure.eventhub import EventHubConsumerClient
from extensions import db, mail, redis_client, WINDOW_SIZE, bot
from models.user import User
from models.device import Device
from models.sensors import Sensor
from models.telemetry import Telemetry
from models.alert_rule import AlertRule
from models.alert import Alert
from models.tg_subscription import TgSubscription
from models.tg_token import TgToken
from dotenv import load_dotenv
import os
from flask import Flask
from sqlalchemy import or_
from datetime import datetime
from flask_mail import Message
import numpy as np
import pandas as pd
from detect_anomaly import detect_anomaly
import asyncio
from deltalake import write_deltalake

load_dotenv()

CONNSECTION_STRING = os.getenv('EVENT_HUB_CONNECTION_STRING')
EVENT_HUB_NAME = os.getenv('EVENT_HUB_NAME')
CONSUMER_GROUP = '$Default'

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
    mail.init_app(app)

    return app

app = create_app()

def check_rule(rule, value):
    if rule.get('min_value') is not None and value < float(rule.get('min_value')):
        return True
    if rule.get('max_value') is not None and value > float(rule.get('max_value')):
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

def send_alert(data):
    try:
        msg = Message(
            subject=f'Alert №{data["alert_id"]}',
            recipients=[data['email']],
            body=(
                f'Alert triggered!\n\n'
                f'Device: #{data["device_id"]}\n'
                f'Sensor: #{data["sensor_id"]}\n'
                f'Time: {data["triggered_at"]}\n'
                f'Value: {data["value"]}\n\n'
                f'Message: {data["message"]}'
            )
        )
        mail.send(msg)
        print('Mail was sent')
    except Exception as e:
        print('Error on sending email:', e)

def update_window(sensor_id, value):
    key = f'anomaly:window:{sensor_id}'
    redis_client.rpush(key, value)
    redis_client.ltrim(key, -WINDOW_SIZE, -1)

def get_window(sensor_id):
    key = f'anomaly:window:{sensor_id}'
    values = redis_client.lrange(key, 0, -1)
    return np.array(values, dtype=np.float32)

def bot_alert(data):
    subscription = TgSubscription.query.filter_by(user_id=data['user_id'], enabled=True).first()
    if not subscription:
        return
    chat_id = subscription.chat_id
    text = (
                f'Alert triggered!\n\n'
                f'Device: #{data["device_id"]}\n'
                f'Sensor: #{data["sensor_id"]}\n'
                f'Time: {data["triggered_at"]}\n'
                f'Value: {data["value"]}\n\n'
                f'Message: {data["message"]}'
            )
    try:
        asyncio.run(bot.send_message(chat_id=chat_id, text=text))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(bot.send_message(chat_id=chat_id, text=text))

def inform_anomaly(user_id, device_id, sensor_id, result):
    subscription = TgSubscription.query.filter_by(user_id=user_id, enabled=True).first()
    if not subscription:
        return
    chat_id = subscription.chat_id
    text = (
        f'Anomal data!\n\n'
        f'Probability: {result["probability"]}\n'
        f'Device: #{device_id}\n'
        f'Sensor: #{sensor_id}\n'
        f'Time: {datetime.utcnow().isoformat()}\n'
    )
    try:
        asyncio.run(bot.send_message(chat_id=chat_id, text=text))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(bot.send_message(chat_id=chat_id, text=text))

def write_raw_to_delta(payload):
    df = pd.DataFrame([{
        'timestamp': payload['timestamp'],
        'sensor_id': payload['sensor'],
        'device_id': payload['device_id'],
        'value': payload['value']
    }])
    write_deltalake(
        'delta/telemetry_raw',
        df,
        mode='append',
        partition_by=['sensor_id']
    )


def on_event(partition_context, event):
    payload = event.body_as_json()
    alerts_to_notify = []
    with app.app_context():
        try:
            model = Telemetry()
            sensor_id = payload['sensor']
            device_id = payload['device_id']
            timestamp = payload['timestamp']
            sensor = redis_client.hgetall(f'sensor:{sensor_id}')
            sensor_name = sensor.get('name')
            device = redis_client.hgetall(f'device:{device_id}')
            Device.query.filter_by(id=device_id).update({
                Device.last_seen_at: datetime.fromisoformat(timestamp)
            })
            user = User.query.filter_by(id=device.get('owner')).first()
            admin = User.query.filter_by(organization=user.organization, access='admin').first()
            rule_ids = set()
            rule_ids |= redis_client.smembers(f'sensor:{sensor_id}:rules')
            rule_ids |= redis_client.smembers(f'sensor:{sensor_name}:rules')
            rule_ids &= redis_client.smembers(f'org:{user.organization}:rules:enabled')
            value = payload['value']
            model.sensor_id = sensor_id
            model.value = value
            model.timestamp = timestamp
            db.session.add(model)
            db.session.flush()
            write_raw_to_delta(payload)
            for rule_id in rule_ids:
                rule = redis_client.hgetall(f'rule:{rule_id}')
                if check_rule(rule, value):
                    if alert_cooldown(rule_id, sensor_id):
                        alert = Alert()
                        alert.rule_id = rule_id
                        alert.sensor_id = sensor_id
                        alert.device_id = device_id
                        alert.value = value
                        alert.triggered_at = datetime.utcnow()
                        alert.resolved = False
                        db.session.add(alert)
                        db.session.flush()
                        alerts_to_notify.append({
                            'alert_id': alert.id,
                            'sensor_id': alert.sensor_id,
                            'device_id': alert.device_id,
                            'value': alert.value,
                            'triggered_at': alert.triggered_at,
                            'email': admin.email,
                            'message': rule.get('message'),
                            'user_id': user.id
                        })
            db.session.commit()
            update_window(sensor_id, value)
            window = get_window(sensor_id)
            if len(window) == WINDOW_SIZE:
                result = detect_anomaly(sensor_id, window)
                redis_client.hset(
                    f'anomaly:result:{sensor_id}',
                    mapping={
                        'score': float(result['score']),
                        'probability': float(result['probability']),
                        'is_anomaly': int(result['is_anomaly']),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                if result['is_anomaly']:
                    inform_anomaly(user.id, device_id, sensor_id, result)
        except KeyboardInterrupt:
            print('Simulation stopped')
        except Exception as e:
            db.session.rollback()
            print('db error:', e)
        finally:
            db.session.remove()
    with app.app_context():
        for alert_data in alerts_to_notify:
            send_alert(alert_data)
            bot_alert(alert_data)

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