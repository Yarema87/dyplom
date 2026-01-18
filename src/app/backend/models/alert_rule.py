from extensions import db

class AlertRule(db.Model):
    __tablename = 'alert_rule'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=True)
    sensor_name = db.Column(db.String(60), nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    message = db.Column(db.Text, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    organization = db.Column(db.String(60), nullable=False)

    sensor = db.relationship('Sensor', back_populates='rule')
    alert = db.relationship('Alert', back_populates='rule')