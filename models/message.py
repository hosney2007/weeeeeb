from extinsion import db

class Message(db.Model):
    __tablename__ ="messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    course = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(150), nullable=False)
    