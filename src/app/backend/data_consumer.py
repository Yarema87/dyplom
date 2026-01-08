from azure.eventhub import EventHubConsumerClient
from extensions import db
from models.user import User
from models.device import Device
from models.sensors import Sensor
from models.telemetry import Telemetry
from models.event_offset import EventOffset
from dotenv import load_dotenv
import os
from flask import Flask
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

def on_event(partition_context, event):
    payload = event.body_as_json()
    seq = event.sequence_number

    with app.app_context():
        offset = EventOffset.query.first()
        last_seq = offset.sequence_number if offset else -1
        if seq <= last_seq:
            partition_context.update_checkpoint(event)
            return
        try:
            model = Telemetry()
            sensor_id = payload['sensor']
            timestamp = payload['timestamp']
            device = Device.query.filter_by(id=payload['device_id']).first()
            device.last_seen_at = datetime.fromisoformat(timestamp)
            value = payload['value']
            model.sensor_id = sensor_id
            model.value = value
            model.timestamp = timestamp
            db.session.add(model)
            print(payload)
            if not offset:
                offset = EventOffset()
                db.session.add(offset)
            offset.sequence_number = seq
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
        starting_position='-1',
    )