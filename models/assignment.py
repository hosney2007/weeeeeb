from extinsion import db

class Assignment(db.Model):
    __tablename__ = "assignment"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey("school_course.id"), nullable=False, index=True)

    questions = db.relationship("Question", backref="assignment", lazy=True, cascade="all,delete")
    submissions = db.relationship("Submission", backref="assignment", lazy=True, cascade="all,delete")
