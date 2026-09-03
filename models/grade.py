from extinsion import db

class Grade(db.Model):
    __tablename__ = "grade"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)

    students = db.relationship("User", backref="grade", lazy=True)
    courses = db.relationship("SchoolCourse", backref="grade", lazy=True, cascade="all,delete")
