#imports=========================///
from flask import Blueprint, jsonify, request, redirect, url_for,render_template,flash
from models.schedaule import Schedule
from models.branch import Branch
from flask_login import login_required
from utils.decorators import admin_required
from models.course import Course
from models.booking import Booking
from extinsion import db
from utils.notifications import notify_student

booking = Blueprint("booking" ,__name__)

#============GET GROUPS====///
@booking.route("/booking/schedules")
def get_schedules():
        
     course_id = request.args.get("course_id")
     mode = request.args.get("mode")
     branch_id = request.args.get("branch_id")
     query = Schedule.query.filter_by(
             course_id=course_id,
             mode=mode
        )
     if mode == "offline":
          query = query.filter_by(branch_id=branch_id)


     schedules = query.all()
     data = []
     for schedule in schedules:
          data.append({
               "id": schedule.id,

               "text" : f"{schedule.level} | "
                       f"{schedule.day1} {schedule.time1} - "
                       f"{schedule.day2} {schedule.time2} "
             })
     return jsonify(data)

#========ADMIN BOOKINGS======///
@booking.route("/admin/booking", methods=["POST", "GET"])
@login_required
@admin_required
def admin_booking():
    bookings = Booking.query.all()
    return render_template("admin/bookings.html" ,booking=bookings, name="Bookings")

#=======APPROVE BOOKING===///
@booking.route("/admin/booking/<int:booking_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = "approved"
    db.session.commit()
    notify_student(
        booking.user,
        title="Your booking has been approved",
        message=f"Your booking for '{booking.course.title}' has been approved. See you in class!",
        link_endpoint="home"
    )
    return redirect(url_for("booking.admin_booking"))

#======[DELETE]====//
@booking.route("/admin/booking/<int:booking_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
            
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for("booking.admin_booking"))
