from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
fernet = Fernet(os.getenv('FERNET_KEY'))