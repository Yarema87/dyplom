from flask import Blueprint
from models.event_offset import EventOffset

mod_offset = Blueprint('offset', __name__, url_prefix='/offset')