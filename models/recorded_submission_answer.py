from extinsion import db


class RecordedSubmissionAnswer(db.Model):
    __tablename__ = "recorded_submission_answer"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("recorded_submission.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("recorded_question.id"), nullable=False, index=True)
    student_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)

    submission = db.relationship(
        "RecordedSubmission",
        backref=db.backref("answers", cascade="all,delete", lazy=True, order_by="RecordedSubmissionAnswer.id")
    )
    question = db.relationship("RecordedQuestion")
