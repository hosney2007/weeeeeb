from extinsion import db

class RecordedSheet(db.Model):
    __tablename__ = "recorded_sheet"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    recorded_course_id = db.Column(db.Integer, db.ForeignKey("recorded.id"), nullable=False, index=True)
