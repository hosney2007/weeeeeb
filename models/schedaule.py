from extinsion import db

class Schedule(db.Model):
    __tablename__ ="schedule"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False, index=True )
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True )
    day1 = db.Column(db.String(20), nullable=False)
    day2 = db.Column(db.String(20), nullable=True)
    time1 = db.Column(db.String(20), nullable=False)
    time2 = db.Column(db.String(20), nullable=True)
    level = db.Column(db.String(30), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    grade = db.Column(db.String(10), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    course = db.relationship("Course", backref="schedule")
   