from datetime import datetime
from extinsion import db


class PendingRegistration(db.Model):
    """A sign-up waiting for email confirmation.

    The real User row is only created once the person clicks the link sent
    to their email, so a wrong/non-existent email never becomes an account.
    """
    __tablename__ = "pending_registration"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    parent_phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(20), default="student")
    grade_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
