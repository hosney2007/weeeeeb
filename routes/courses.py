#imports============///
from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime
from models.course import Course
from models.schedaule import Schedule
from utils.decorators import admin_required

course = Blueprint("course", __name__)


def _format_time(value):
    """'17:00' -> '5:00 PM'. Falls back to the raw value if it's not HH:MM."""
    try:
        parsed = datetime.strptime(value, "%H:%M")
    except (ValueError, TypeError):
        return value
    # %-I/%#I (no leading zero) aren't portable across Linux and Windows,
    # so format with the zero and strip it ourselves instead.
    formatted = parsed.strftime("%I:%M %p")
    return formatted.lstrip("0")

@course.route("/admin/course", methods=["POST", "GET"])
@login_required
@admin_required
def courses():
    course = Course.query.all()
    return render_template("admin/course.html" ,course=course, name= "Courses")

@course.route("/courses/offline")
def offline_courses():
    courses = Course.query.filter_by(course_type="offline", is_active=True).all()

    # لكل كورس، نجيب كل الجروبات الأوفلاين المسجلة عليه (مستوى + فرع + مواعيد)
    # عشان الكارت يعرض تفاصيل حقيقية بدل وصف عام بس
    course_details = {}
    for c in courses:
        schedules = Schedule.query.filter_by(course_id=c.id, mode="offline").all()
        course_details[c.id] = [
            {
                "level": s.level,
                "branch": s.branch.name if s.branch else None,
                "day1": s.day1,
                "time1": _format_time(s.time1),
                "day2": s.day2,
                "time2": _format_time(s.time2),
            }
            for s in schedules
        ]

    return render_template("offline.html", course=courses, course_details=course_details)

@course.route("/courses/online")
def online_courses():
    courses = Course.query.filter_by(course_type="online", is_active=True).all()

    course_details = {}
    for c in courses:
        schedules = Schedule.query.filter_by(course_id=c.id, mode="online").all()
        course_details[c.id] = [
            {
                "level": s.level,
                "day1": s.day1,
                "time1": _format_time(s.time1),
                "day2": s.day2,
                "time2": _format_time(s.time2),
            }
            for s in schedules
        ]

    return render_template("online.html", course=courses, course_details=course_details)

