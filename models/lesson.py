from extinsion import db

class Lessons(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    video_links = db.Column(db.Text, nullable=False)
    lesson_order = db.Column(db.Integer,nullable=True)
    recorded_course_id = db.Column(db.Integer, db.ForeignKey("recorded.id"), nullable=False, index=True )

