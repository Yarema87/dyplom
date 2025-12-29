from flask import g, Blueprint

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

@mod_auth.route('/auth')
def check_auth():
    if g.user is None:
        return {'authenticated': False}, 200
    else:
        return {
            'authenticated': True,
            'user': {
                'id': g.user['user_id'],
                'email': g.user['email'],
                'organization': g.user.get('organization'),
                'access': g.user['access']
            }
        }, 200