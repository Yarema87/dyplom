from flask import Blueprint
from models.device_credentials import DeviceCredentials

mod_credentials = Blueprint('device_credentials', __name__, url_prefix='/credentials')