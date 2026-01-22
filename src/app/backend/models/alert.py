from extensions import db

class Alert(db.Model):
    __tablename = 'alert'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rule.id'))
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    value = db.Column(db.Float)
    triggered_at = db.Column(db.DateTime)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    rule = db.relationship('AlertRule', back_populates='alert')
    sensor = db.relationship('Sensor', back_populates='alert')
    device = db.relationship('Device', back_populates='alert')