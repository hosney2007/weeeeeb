#imoprts========================//
from flask import Blueprint, render_template,redirect,url_for,flash
from models.message import Message
from flask_login import login_required
from extinsion import db
from utils.decorators import admin_required


message = Blueprint("message",__name__)

@message.route("/admin/message" ,methods=["GET"])
@login_required
@admin_required
def contact():
    message = Message.query.all()
    return render_template("admin/contact.html", message=message, name="message")

@message.route("/admin/message/<int:message_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
            
    db.session.delete(message)
    db.session.commit()
    flash("message deleted","success")
    return redirect(url_for("message.contact"))
