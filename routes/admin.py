#imoprts=============================///
from flask import Blueprint, render_template, request, redirect, url_for,flash
from flask_login import  current_user, login_required
from extinsion import db
from models.course import Course
from models.booking import Booking
from models.purchase import Purchase
from models.recorded import Recorded
from models.user import User
from  models.message import Message
from datetime import datetime
from models.branch import Branch
from models.schedaule import Schedule
from models.success_story import SuccessStory
from models.book_purchase import BookPurchase
from utils.decorators import admin_required
from utils.uploads import upload_course_image


admin = Blueprint("admin" ,__name__)
# ===================admindashboard==========////
@admin.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    courses = Course.query.filter_by(is_active=True).all()

    total_courses = len(courses)

    active_students = User.query.filter_by(
        role="student",
        is_verified=True
    ).count()

    pending_bookings = Booking.query.filter_by(
        status="pending"
    ).count()

    pending_orders = Purchase.query.filter(
        Purchase.status.in_(["pending", "waiting"])
    ).count()

    approved_orders = Purchase.query.filter_by(
        status="approved"
    ).all()

    monthly_revenue = sum(
        float(order.recorded.price or 0)
        for order in approved_orders
        if order.recorded
    )

    today_name = datetime.now().strftime("%A")

    today_schedules = []
    for schedule in Schedule.query.all():
        # Match against day1/time1 or day2/time2 separately so the widget
        # shows the slot that's actually happening today, not always the
        # first one on the schedule.
        if today_name.lower() == (schedule.day1 or "").strip().lower():
            today_schedules.append({
                "schedule": schedule,
                "day": schedule.day1,
                "time": schedule.time1
            })
        elif today_name.lower() == (schedule.day2 or "").strip().lower():
            today_schedules.append({
                "schedule": schedule,
                "day": schedule.day2,
                "time": schedule.time2
            })

    today_schedule_ids = {
        entry["schedule"].id
        for entry in today_schedules
    }

    today_bookings = (
        Booking.query.filter(
            Booking.schedule_id.in_(today_schedule_ids)
        ).count()
        if today_schedule_ids
        else 0
    )

    pending_book_orders = BookPurchase.query.filter(
        BookPurchase.status.in_(["pending", "waiting"])
    ).count()

    total_messages = Message.query.count()

    recent_bookings = Booking.query.order_by(
        Booking.id.desc()
    ).limit(4).all()

    recent_orders = Purchase.query.order_by(
        Purchase.id.desc()
    ).limit(4).all()

    recent_messages = Message.query.order_by(
        Message.id.desc()
    ).limit(4).all()

    return render_template(
        "admin/admin-dashboard.html",
        user=current_user,
        course=courses,
        name="Admin",
        total_courses=total_courses,
        active_students=active_students,
        pending_bookings=pending_bookings,
        pending_orders=pending_orders,
        pending_book_orders=pending_book_orders,
        monthly_revenue=monthly_revenue,
        today_bookings=today_bookings,
        today_schedules=today_schedules,
        total_messages=total_messages,
        recent_bookings=recent_bookings,
        recent_orders=recent_orders,
        recent_messages=recent_messages
    )

#==============verified students==================////

@admin.route("/admin/students")
@login_required
@admin_required
def verified_students():
    students = User.query.filter_by(
        role="student",
        is_verified=True
    ).order_by(User.name.asc()).all()

    return render_template(
        "admin/students.html",
        students=students,
        name="Verified Students"
    )

#==============addd courses==================////

@admin.route("/admin/add-course", methods=["GET", "POST"])
@login_required
@admin_required
def add_course():
    if request.method == "POST":
        image = request.files.get("image")
        image_url = upload_course_image(image)
        title = request.form["title"]
        description = request.form["description"]
        course_type = request.form["course_type"]    
        course = Course(
            title = title,
            description= description,
            course_type=course_type,
            image=image_url
        )  
        db.session.add(course)
        db.session.commit()
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("admin/add-course.html", name="add Course")      

#edit courses
@admin.route("/admin/edit-course/<int:course_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_course( course_id ):
    course = Course.query.get_or_404(course_id)
    if request.method == "POST":

        course.title = request.form["title"]
        course.description = request.form["description"]
        course.course_type = request.form["course_type"]

        db.session.commit()
        flash("course edited", "success")
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("admin/edit-course.html", course=course, name="Edit Course")   


#=================delete courses=========//////
@admin.route("/admin/delete-course/<int:course_id>", methods=["POST"])
@login_required
@admin_required
def delete_course( course_id ):
    course = Course.query.get_or_404(course_id)
    if course.schedule:
        flash("you can't delete this course because it has groups","danger")
        return redirect(url_for("course.courses"))
        
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

#==============================groups===============================================
#=========add group=========///
@admin.route("/admin/add-group", methods=["GET", "POST"])
@login_required
@admin_required
def add_group():
    courses = Course.query.all()
    branches = Branch.query.all()
    if request.method == "POST":

        course_id = request.form.get("course_id")
        level = request.form.get("level")
        mode = request.form.get("mode")
        branch_id = request.form.get("branch_id")
        day1 = request.form.get("day1")
        time1 = request.form.get("time1")
        day2 = request.form.get("day2")
        time2 = request.form.get("time2")
        if mode == "online":
            branch_id = None
        
    
        schedule = Schedule(
            course_id=course_id,
            level=level,
            mode=mode,
            branch_id=branch_id,
            day1=day1,
            time1=time1,
            day2=day2,
            time2=time2

        )  
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("admin/add-group.html", course=courses, branches=branches, name="Add Group")      


#====branch==////
@admin.route("/admin/branch", methods=["POST", "GET"])
@login_required
@admin_required
def branch():
    branch = Branch.query.all()
    return render_template("admin/branch.html" ,branch=branch, name= "Branches")

@admin.route("/admin/add-branch", methods=["GET", "POST"])
@login_required
@admin_required
def add_branch():
    if request.method == "POST":

        name = request.form.get("name")
        branch = Branch(
            name=name
        )
            
        db.session.add(branch)
        db.session.commit()
        return redirect(url_for("admin.branch"))
    return render_template("admin/add-branch.html")  

@admin.route("/admin/delete-branch/<int:branch_id>", methods=["POST"])
@login_required
@admin_required
def delete_branch( branch_id ):
    branch = Branch.query.get_or_404(branch_id)
    if branch.schedule:
        flash("you can't delete this course because it has groups","danger")
        return redirect(url_for("admin.branch"))
        
    db.session.delete(branch)
    db.session.commit()
    return redirect(url_for("admin.branch"))


#========successs story====///
@admin.route("/success-stories")
@login_required
@admin_required
def success_stories():

    stories = SuccessStory.query.order_by(
        SuccessStory.id.desc()
    ).all()

    return render_template(
        "admin/success_stories.html",
        stories=stories,
        name="Success Stories"
    )
#add===============
@admin.route("/success-stories/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_success_story():

    if request.method == "POST":

        student_name = request.form.get("student_name", "").strip()
        subject = request.form.get("subject", "").strip()
        before_score_raw = request.form.get("before_score", "").strip()
        after_score_raw = request.form.get("after_score", "").strip()
        review = request.form.get("review", "").strip()

        if not student_name or not subject or not review:
            flash("Please fill in all the fields.", "danger")
            return redirect(url_for("admin.add_success_story"))

        try:
            before_score = int(before_score_raw)
            after_score = int(after_score_raw)
        except ValueError:
            flash("Scores must be whole numbers.", "danger")
            return redirect(url_for("admin.add_success_story"))

        image = request.files.get("image")

        if not image or not image.filename:
            flash("Please choose an image.", "danger")
            return redirect(url_for("admin.add_success_story"))

        image_url = upload_course_image(image, folder="success_stories")

        if not image_url:
            # upload_course_image already flashed the specific reason
            # (invalid file type, invalid image, etc.)
            return redirect(url_for("admin.add_success_story"))

        story = SuccessStory(

            student_name=student_name,

            subject=subject,

            before_score=before_score,

            after_score=after_score,

            review=review,

            image=image_url

        )

        db.session.add(story)

        db.session.commit()

        flash("Success story added successfully.", "success")

        return redirect(url_for("admin.success_stories"))

    return render_template(
        "admin/add_success_story.html",
        name="Add Success Story"
    )
# edit============
@admin.route("/success-stories/edit/<int:story_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_success_story(story_id):

    story = SuccessStory.query.get_or_404(story_id)

    if request.method == "POST":

        student_name = request.form.get("student_name", "").strip()
        subject = request.form.get("subject", "").strip()
        before_score_raw = request.form.get("before_score", "").strip()
        after_score_raw = request.form.get("after_score", "").strip()
        review = request.form.get("review", "").strip()

        if not student_name or not subject or not review:
            flash("Please fill in all the fields.", "danger")
            return redirect(url_for("admin.edit_success_story", story_id=story_id))

        try:
            before_score = int(before_score_raw)
            after_score = int(after_score_raw)
        except ValueError:
            flash("Scores must be whole numbers.", "danger")
            return redirect(url_for("admin.edit_success_story", story_id=story_id))

        image = request.files.get("image")

        if image and image.filename:
            new_image_url = upload_course_image(image, folder="success_stories")
            if not new_image_url:
                # upload_course_image already flashed the specific reason
                return redirect(url_for("admin.edit_success_story", story_id=story_id))
            story.image = new_image_url

        story.student_name = student_name
        story.subject = subject
        story.before_score = before_score
        story.after_score = after_score
        story.review = review

        db.session.commit()

        flash("Success story updated successfully.", "success")

        return redirect(url_for("admin.success_stories"))

    return render_template(
        "admin/edit_success_story.html",
        story=story,
        name="Edit Success Story"
    )
#delete====================
@admin.route("/success-stories/delete/<int:story_id>", methods=["POST"])
@login_required
@admin_required
def delete_success_story(story_id):

    story = SuccessStory.query.get_or_404(story_id)

    db.session.delete(story)

    db.session.commit()

    flash("Success story deleted successfully.", "success")

    return redirect(url_for("admin.success_stories"))