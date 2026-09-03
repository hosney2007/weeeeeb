from extinsion import db
class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True ,unique=True)
    # No delete cascade here on purpose: routes.admin.delete_branch already
    # blocks deletion while schedules exist, and schedules can have bookings
    # pointing at them with no cascade of their own. A cascade here would let
    # a branch delete silently orphan booking rows if that guard is ever
    # bypassed (e.g. a future code path, or a direct DB/shell delete).
    schedule = db.relationship("Schedule", backref="branch", lazy=True)
