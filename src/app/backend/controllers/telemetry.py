from flask import Blueprint
from models.telemetry import Telemetry

mod_telemetry = Blueprint('telemetry', __name__, url_prefix='/telemetry')