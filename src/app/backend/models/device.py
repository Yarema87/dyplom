from extensions import db

class Device(db.Model):
    __tablename = 'device'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20))
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.String(20), nullable=False)
    last_seen_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connection_id = db.Column(db.String(100), nullable=False)

    owner = db.relationship('User', back_populates='device')
    sensors = db.relationship('Sensor', back_populates='device', cascade='all, delete-orphan')