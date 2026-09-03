from extinsion import db

class SchoolSheet(db.Model):
    __tablename__ = "school_sheet"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("school_course.id"), nullable=False, index=True)
