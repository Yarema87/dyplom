from extensions import db

class TgSubscription(db.Model):
    __tablename = 'tg_subscription'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='subscription')