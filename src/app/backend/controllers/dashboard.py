from flask import g, Blueprint
from user_check import login_required

mod_dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@mod_dashboard.route('/dashboard')
@login_required
def dashboard():
    return {
        'message': 'Welcome',
        'user': g.user
    }