
from extinsion import db
class SuccessStory(db.Model):
    __tablename__ = "success_stories"

    id = db.Column(db.Integer, primary_key=True)

    student_name = db.Column(db.String(100), nullable=False)

    subject = db.Column(db.String(100), nullable=False)

    before_score = db.Column(db.Integer, nullable=False)

    after_score = db.Column(db.Integer, nullable=False)

    review = db.Column(db.Text, nullable=False)

    image = db.Column(db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    