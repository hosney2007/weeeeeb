from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from extinsion import db
from models.notification import Notification

notifications = Blueprint("notifications", __name__)


@notifications.route("/notifications")
@login_required
def list_notifications():
    items = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()

    unread_ids = [n.id for n in items if not n.is_read]
    if unread_ids:
        Notification.query.filter(Notification.id.in_(unread_ids)).update(
            {"is_read": True}, synchronize_session=False
        )
        db.session.commit()

    return render_template("notifications.html", notifications=items, name="Notifications")


@notifications.route("/notifications/<int:id>/open")
@login_required
def open_notification(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id != current_user.id:
        return redirect(url_for("notifications.list_notifications"))

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return redirect(notification.link or url_for("notifications.list_notifications"))
