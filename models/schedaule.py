from extinsion import db

class Schedule(db.Model):
    __tablename__ ="schedule"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False, index=True )
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True )
    day1 = db.Column(db.String(20), nullable=False)
    day2 = db.Column(db.String(20), nullable=False)
    time1 = db.Column(db.String(20), nullable=False)
    time2 = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(30), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    course = db.relationship("Course", backref="schedule")
   