from extensions import db

class EventOffset(db.Model):
    __tablename = 'offset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sequence_number = db.Column(db.BigInteger)
