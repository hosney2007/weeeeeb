from extinsion import db

class Booking(db.Model):
    __tablename__ ="bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_number = db.Column(db.String(20), nullable=False)
    parent_number = db.Column(db.String(20), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    addational_notes = db.Column(db.String(150), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False, index=True )
    schedule_id = db.Column(db.Integer, db.ForeignKey("schedule.id"), nullable=False, index=True )
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True )
    mode = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending" ,nullable=False)
    
    user = db.relationship("User", backref="bookings")
    branch = db.relationship("Branch", backref="bookings")
    course = db.relationship("Course", backref="bookings")
    schedule = db.relationship("Schedule", backref="bookings")

