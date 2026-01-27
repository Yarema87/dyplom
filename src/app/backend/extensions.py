from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from cryptography.fernet import Fernet
import redis
import joblib
from keras.models import load_model
import os
from dotenv import load_dotenv
import pandas as pd
from telegram import Bot

load_dotenv()

db = SQLAlchemy()
fernet = Fernet(os.getenv('FERNET_KEY'))
mail = Mail()

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'anomaly_model.keras')
scaler_path = os.path.join(BASE_DIR, 'scalers.pkl')
threshold_path = os.path.join(BASE_DIR, 'thresholds.pkl')
csv_path = os.path.join(BASE_DIR, 'telemetry.csv')

neuromodel = load_model(model_path, compile=False)
scalers = joblib.load(scaler_path)
thresholds = joblib.load(threshold_path)
df = pd.read_csv(csv_path)

WINDOW_SIZE = 30

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
