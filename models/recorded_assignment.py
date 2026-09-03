from extinsion import db

class RecordedAssignment(db.Model):
    __tablename__ = "recorded_assignment"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    recorded_course_id = db.Column(db.Integer, db.ForeignKey("recorded.id"), nullable=False, index=True)

    questions = db.relationship("RecordedQuestion", backref="assignment", lazy=True, cascade="all,delete")
    submissions = db.relationship("RecordedSubmission", backref="assignment", lazy=True, cascade="all,delete")
