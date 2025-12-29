from extensions import db

class DeviceCredentials(db.Model):
    __tablename = 'device_credentials'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    provider = db.Column(db.String(30), nullable=False)
    connection_string = db.Column(db.String(150))
    
    device = db.relationship('Device', back_populates='credentials')
