from extinsion import db


class SubmissionAnswer(db.Model):
    __tablename__ = "submission_answer"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submission.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False, index=True)
    student_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)

    submission = db.relationship(
        "Submission",
        backref=db.backref("answers", cascade="all,delete", lazy=True, order_by="SubmissionAnswer.id")
    )
    question = db.relationship("Question")
