from extinsion import db

class SchoolCourse(db.Model):
    __tablename__ = "school_course"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False, index=True)

    lessons = db.relationship("SchoolLesson", backref="course", lazy=True, cascade="all,delete", order_by="SchoolLesson.order")
    sheets = db.relationship("SchoolSheet", backref="course", lazy=True, cascade="all,delete")
    assignments = db.relationship("Assignment", backref="course", lazy=True, cascade="all,delete")
