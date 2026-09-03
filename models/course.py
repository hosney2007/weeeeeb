from extinsion import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False) 
    description = db.Column(db.Text, nullable=False) 
    course_type = db.Column(db.String(20), nullable=False) 
    image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)