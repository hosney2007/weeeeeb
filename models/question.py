from extinsion import db

class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False, default="mcq")  # mcq | text
    options = db.Column(db.Text, nullable=True)  # options separated by "||" (mcq only)
    correct_answer = db.Column(db.String(255), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False, index=True)

    def options_list(self):
        if not self.options:
            return []
        return [o.strip() for o in self.options.split("||") if o.strip()]
