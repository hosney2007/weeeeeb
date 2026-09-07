#imports============///
from flask import Blueprint, render_template
from flask_login import login_required
from models.course import Course
from models.schedaule import Schedule
from utils.decorators import admin_required

course = Blueprint("course", __name__)

@course.route("/admin/course", methods=["POST", "GET"])
@login_required
@admin_required
def courses():
    course = Course.query.all()
    return render_template("admin/course.html" ,course=course, name= "Courses")

@course.route("/courses/offline")
def offline_courses():
    courses = Course.query.filter_by(course_type="offline", is_active=True).all()

    # لكل كورس، نجيب الفروع والمستويات المتاحة له من الجروبات الأوفلاين
    # المسجلة عليه، عشان الكارت يعرض تفاصيل حقيقية بدل وصف عام بس
    course_details = {}
    for c in courses:
        schedules = Schedule.query.filter_by(course_id=c.id, mode="offline").all()
        course_details[c.id] = {
            "branches": sorted({s.branch.name for s in schedules if s.branch}),
            "levels": sorted({s.level for s in schedules if s.level})
        }

    return render_template("offline.html", course=courses, course_details=course_details)

@course.route("/courses/online")
def online_courses():
    courses = Course.query.filter_by(course_type="online").all()
    return render_template("online.html", course=courses)

