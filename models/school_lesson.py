from extinsion import db

class SchoolLesson(db.Model):
    __tablename__ = "school_lesson"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("school_course.id"), nullable=False, index=True)
    order = db.Column(db.Integer, default=1)
