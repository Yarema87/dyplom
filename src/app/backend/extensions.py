from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from cryptography.fernet import Fernet
import redis
import os
from dotenv import load_dotenv

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