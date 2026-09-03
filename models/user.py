from extinsion import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True ,nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column( db.String(20), default="student")
    is_verified= db.Column(db.Boolean, default=False)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=True, index=True)
    purchase = db.relationship("Purchase", backref="user", lazy=True)
