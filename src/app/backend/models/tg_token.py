from extensions import db

class TgToken(db.Model):
    __tablename = 'tg_token'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(60))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime)
    used = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='tg_token')