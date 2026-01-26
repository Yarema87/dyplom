from extensions import db

class User(db.Model):
    __tablename = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(50))
    access = db.Column(db.String(5), nullable=False)
    approved = db.Column(db.Boolean)

    device = db.relationship('Device', back_populates='owner')
    subscription = db.relationship('TgSubscription', back_populates='user') 
    tg_token = db.relationship('TgToken', back_populates='user')
