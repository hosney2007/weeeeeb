from flask import current_app, url_for
from flask_mail import Message
from extinsion import db, mail
from models.notification import Notification


def notify_admin(subject, lines):
    """
    Sends a plain-text email to ADMIN_EMAIL. `lines` is a list of
    "label: value" strings shown one per line in the email body.
    Never raises - a broken mail server shouldn't break the purchase/booking
    flow itself, so failures are logged instead.
    """
    admin_email = current_app.config.get("ADMIN_EMAIL")
    if not admin_email:
        return

    try:
        msg = Message(subject=subject, recipients=[admin_email])
        msg.body = "\n".join(lines)
        mail.send(msg)
    except Exception as e:
        current_app.logger.error("Failed to send admin notification email: %s", e)


def notify_student(user, title, message, link_endpoint=None, link_kwargs=None, send_email=True):
    """
    Creates an in-app Notification for the student, and optionally emails
    them too. `link_endpoint`/`link_kwargs` build the notification's link via
    url_for so it always points to a real route.
    `user` can be None (e.g. a guest booking with no linked account) - in
    that case there's nowhere to deliver a notification, so this is a no-op.
    """
    if user is None:
        return

    link = None
    if link_endpoint:
        try:
            link = url_for(link_endpoint, **(link_kwargs or {}))
        except Exception:
            link = None

    notification = Notification(
        user_id=user.id,
        title=title,
        message=message,
        link=link
    )
    db.session.add(notification)
    db.session.commit()

    if send_email and user.email:
        try:
            msg = Message(subject=title, recipients=[user.email])
            msg.body = message
            mail.send(msg)
        except Exception as e:
            current_app.logger.error("Failed to send student notification email: %s", e)
