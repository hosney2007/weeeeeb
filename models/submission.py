from extinsion import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = "submission"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False, index=True)
    score = db.Column(db.Float, default=0)
    total = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("User", backref="submissions", lazy=True)
