#imports======================///
from flask import Blueprint, render_template,redirect,url_for,flash
from flask_login import login_required
from utils.decorators import admin_required
from models.schedaule import Schedule
from extinsion import db

schedule = Blueprint("schedule", __name__)
#======= SHOW GROUPS===///
@schedule.route("/admin/schedule")
@login_required
@admin_required
def show_schedule():
    schedules = Schedule.query.all()
    return render_template("admin/schedules.html" , schedule=schedules, name="Groups")

#=====DELTE GROUPS=======//
@schedule.route("/admin/schedule/<int:schedule_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.bookings:
        flash("you can't delete this group because it has booking","danger")
        return redirect(url_for("schedule.show_schedule"))    
    db.session.delete(schedule)
    db.session.commit()
    return redirect(url_for("schedule.show_schedule"))


