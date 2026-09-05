#imports=============================///
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extinsion import db
from models.school_course import SchoolCourse
from models.school_lesson import SchoolLesson
from models.school_sheet import SchoolSheet
from models.assignment import Assignment
from models.question import Question
from models.submission import Submission
from models.submission_answer import SubmissionAnswer
from utils.decorators import school_student_required
from models.recorded import Recorded
from models.booking import Booking
from models.purchase import Purchase
from flask_mail import Message

school = Blueprint("school", __name__, url_prefix="/school")


def _grade_courses():
    """كل الكورسات الخاصة بـ Grade الطالب الحالي فقط."""
    return SchoolCourse.query.filter_by(grade_id=current_user.grade_id).all()


#======DASHBOARD=====///
@school.route("/dashboard")
@login_required
@school_student_required
def dashboard():
    courses = _grade_courses()
    course_ids = [c.id for c in courses]

    user = current_user

    assignments = Assignment.query.filter(
        Assignment.course_id.in_(course_ids)
    ).all() if course_ids else []

    purchases = Purchase.query.filter_by(
        user_id=current_user.id,
        status="approved"
    ).all()

    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    submitted_ids = {
        s.assignment_id for s in Submission.query.filter_by(student_id=current_user.id).all()
    }

    total_recorded = len(purchases)
    total_bookings = len(bookings)

    pending_assignments = [a for a in assignments if a.id not in submitted_ids]

    pending_bookings = sum(1 for b in bookings if b.status == "pending")
    approved_bookings = sum(1 for b in bookings if b.status == "approved")

    return render_template(
        "school/dashboard.html",
        name="Dashboard",
        courses=courses,
        total_courses=len(courses),
        total_assignments=len(assignments),
        pending_assignments=pending_assignments,
        user=user,
        purchases=purchases,
        bookings=bookings,
        total_recorded=total_recorded,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings    )


#======COURSES=====///
@school.route("/courses")
@login_required
@school_student_required
def courses():
    courses = _grade_courses()
    return render_template("school/courses.html", name="Courses", courses=courses)


@school.route("/course/<int:id>")
@login_required
@school_student_required
def course(id):
    course = SchoolCourse.query.get_or_404(id)
    if course.grade_id != current_user.grade_id:
        abort(403)
    return render_template("school/course.html", name=course.name, course=course)


#======LESSON=====///
@school.route("/lessons/<int:id>")
@login_required
@school_student_required
def lesson(id):
    lesson = SchoolLesson.query.get_or_404(id)

    lenght=SchoolLesson.query.filter_by(
        course_id=lesson.course_id
    ).count()
    
    if lesson.course.grade_id != current_user.grade_id:
        abort(403)
    return render_template("school/lesson.html", name=lesson.title, lesson=lesson, lenght=lenght)


#======SHEETS=====///
@school.route("/sheets")
@login_required
@school_student_required
def sheets():
    courses = _grade_courses()
    sheets = SchoolSheet.query.filter(
        SchoolSheet.course_id.in_([c.id for c in courses])
    ).all() if courses else []
    return render_template("school/sheets.html", name="Sheets", sheets=sheets)


#======ASSIGNMENTS=====///
@school.route("/assignments")
@login_required
@school_student_required
def assignments():
    courses = _grade_courses()
    assignments = Assignment.query.filter(
        Assignment.course_id.in_([c.id for c in courses])
    ).all() if courses else []

    submissions = {
        s.assignment_id: s for s in Submission.query.filter_by(student_id=current_user.id).all()
    }

    return render_template(
        "school/assignments.html",
        name="Assignments",
        assignments=assignments,
        submissions=submissions
    )


@school.route("/assignment/<int:id>")
@login_required
@school_student_required
def assignment(id):
    assignment = Assignment.query.get_or_404(id)
    if assignment.course.grade_id != current_user.grade_id:
        abort(403)

    existing = Submission.query.filter_by(
        student_id=current_user.id, assignment_id=id
    ).first()

    if existing:
        return redirect(url_for("school.assignment_result", id=existing.id))

    return render_template(
        "school/assignment.html",
        name=assignment.title,
        assignment=assignment
    )


#======SUBMIT=====///
@school.route("/assignment/<int:id>/submit", methods=["POST"])
@login_required
@school_student_required
def submit_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    if assignment.course.grade_id != current_user.grade_id:
        abort(403)

    existing = Submission.query.filter_by(
        student_id=current_user.id, assignment_id=id
    ).first()
    if existing:
        flash("You already submitted this assignment.", "warning")
        return redirect(url_for("school.assignment_result", id=existing.id))

    questions = assignment.questions
    correct_count = 0

    submission = Submission(
        student_id=current_user.id,
        assignment_id=id,
        score=0,
        total=len(questions)
    )
    db.session.add(submission)

    for question in questions:
        answer = request.form.get(f"question_{question.id}", "").strip()
        is_correct = answer.lower() == (question.correct_answer or "").strip().lower()
        if is_correct:
            correct_count += 1

        db.session.add(SubmissionAnswer(
            submission=submission,
            question_id=question.id,
            student_answer=answer,
            is_correct=is_correct
        ))

    total = len(questions)
    submission.score = round((correct_count / total) * 100, 2) if total else 0

    db.session.commit()

    flash("Assignment submitted successfully.", "success")
    return redirect(url_for("school.assignment_result", id=submission.id))


@school.route("/assignment/result/<int:id>")
@login_required
@school_student_required
def assignment_result(id):
    submission = Submission.query.get_or_404(id)
    if submission.student_id != current_user.id:
        abort(403)
    return render_template(
        "school/result.html",
        name="Result",
        submission=submission
    )


#======PROGRESS=====///
@school.route("/progress")
@login_required
@school_student_required
def progress():
    courses = _grade_courses()
    course_ids = [c.id for c in courses]

    assignments = Assignment.query.filter(
        Assignment.course_id.in_(course_ids)
    ).all() if course_ids else []

    submissions = Submission.query.filter_by(student_id=current_user.id).all()
    submitted_ids = {s.assignment_id for s in submissions}

    assignments_completed = len(submissions)
    average_score = round(
        sum(s.score for s in submissions) / len(submissions), 2
    ) if submissions else 0

    course_progress = []
    for course in courses:
        course_assignments = [a for a in assignments if a.course_id == course.id]
        done = len([a for a in course_assignments if a.id in submitted_ids])
        percent = round((done / len(course_assignments)) * 100) if course_assignments else 0
        course_progress.append({
            "course": course,
            "done": done,
            "total": len(course_assignments),
            "percent": percent
        })

    return render_template(
        "school/progress.html",
        name="Progress",
        assignments_completed=assignments_completed,
        average_score=average_score,
        course_progress=course_progress
    )
