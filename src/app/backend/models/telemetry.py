from extensions import db

class Telemetry(db.Model):
    __tablename = 'telemetry'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    value = db.Column(db.Double, nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)

    sensor = db.relationship('Sensor', back_populates='telemetry')
