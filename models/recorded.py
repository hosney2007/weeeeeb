from extinsion import db
from models.lesson import Lessons
class Recorded(db.Model):
    __tablename__ = "recorded"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False) 
    description = db.Column(db.Text) 
    price = db.Column(db.Float, nullable=True) 
    thumbnail = db.Column(db.String(255), nullable=True)

    lessons = db.relationship("Lessons", backref="recorded", cascade="all, delete-orphan")
    purchase = db.relationship("Purchase", backref="recorded", lazy=True)
    sheets = db.relationship("RecordedSheet", backref="recorded", cascade="all, delete-orphan")
    assignments = db.relationship("RecordedAssignment", backref="recorded", cascade="all, delete-orphan")

