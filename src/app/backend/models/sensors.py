from extensions import db

class Sensor(db.Model):
    __tablename = 'sensor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    data_type = db.Column(db.String(10), nullable=False)
    min_value = db.Column(db.Integer)
    max_value = db.Column(db.Integer)

    device = db.relationship('Device', back_populates='sensors')