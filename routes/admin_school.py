#imports=============================///
import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extinsion import db
from models.grade import Grade
from models.user import User
from models.school_course import SchoolCourse
from models.school_lesson import SchoolLesson
from models.school_sheet import SchoolSheet
from models.assignment import Assignment
from models.question import Question
from utils.decorators import admin_required, save_sheet_file

school_admin = Blueprint("school_admin", __name__, url_prefix="/school-admin")


def _generate_grade_code(name):
    base = "".join(c for c in name.upper() if c.isalnum())[:4] or "GRD"
    while True:
        code = f"{base}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        if not Grade.query.filter_by(code=code).first():
            return code


#======GRADES=====///
@school_admin.route("/grades", methods=["GET", "POST"])
@login_required
@admin_required
def grades():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Grade name is required.", "danger")
            return redirect(url_for("school_admin.grades"))
        if Grade.query.filter_by(name=name).first():
            flash("This grade already exists.", "danger")
            return redirect(url_for("school_admin.grades"))

        grade = Grade(name=name, code=_generate_grade_code(name))
        db.session.add(grade)
        db.session.commit()
        flash(f"Grade added. Code: {grade.code}", "success")
        return redirect(url_for("school_admin.grades"))

    grades = Grade.query.all()
    return render_template("admin/school/grades.html", name="Grades", grades=grades)


@school_admin.route("/grades/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    if grade.courses or grade.students:
        flash("You can't delete a grade that has students or courses.", "danger")
        return redirect(url_for("school_admin.grades"))
    db.session.delete(grade)
    db.session.commit()
    flash("Grade deleted.", "success")
    return redirect(url_for("school_admin.grades"))


#======STUDENTS=====///
@school_admin.route("/students")
@login_required
@admin_required
def students():
    students = User.query.filter_by(role="school_student").all()
    return render_template("admin/school/students.html", name="Students", students=students)


#======COURSES=====///
@school_admin.route("/courses", methods=["GET", "POST"])
@login_required
@admin_required
def courses():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        grade_id = request.form.get("grade_id")

        if not name or not grade_id:
            flash("Course name and grade are required.", "danger")
            return redirect(url_for("school_admin.courses"))

        course = SchoolCourse(name=name, description=description, grade_id=grade_id)
        db.session.add(course)
        db.session.commit()
        flash("Course added.", "success")
        return redirect(url_for("school_admin.courses"))

    courses = SchoolCourse.query.all()
    grades = Grade.query.all()
    return render_template(
        "admin/school/courses.html", name="School Courses", courses=courses, grades=grades
    )


@school_admin.route("/courses/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_course(id):
    course = SchoolCourse.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted.", "success")
    return redirect(url_for("school_admin.courses"))


#======LESSONS=====///
@school_admin.route("/courses/<int:id>/lessons", methods=["GET", "POST"])
@login_required
@admin_required
def lessons(id):
    course = SchoolCourse.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        video_url = request.form.get("video_url", "").strip()
        description = request.form.get("description", "").strip()
        order_raw = request.form.get("order", "").strip()

        if not title or not video_url:
            flash("Lesson title and video url are required.", "danger")
            return redirect(url_for("school_admin.lessons", id=course.id))

        try:
            order = int(order_raw) if order_raw else len(course.lessons) + 1
        except ValueError:
            flash("Order must be a whole number.", "danger")
            return redirect(url_for("school_admin.lessons", id=course.id))

        lesson = SchoolLesson(
            title=title, description=description, video_url=video_url,
            course_id=course.id, order=order
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Lesson added.", "success")
        return redirect(url_for("school_admin.lessons", id=course.id))

    return render_template("admin/school/lessons.html", name="Lessons", course=course)


@school_admin.route("/lessons/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_lesson(id):
    lesson = SchoolLesson.query.get_or_404(id)
    course_id = lesson.course_id
    db.session.delete(lesson)
    db.session.commit()
    flash("Lesson deleted.", "success")
    return redirect(url_for("school_admin.lessons", id=course_id))


#======SHEETS=====///
@school_admin.route("/courses/<int:id>/sheets", methods=["GET", "POST"])
@login_required
@admin_required
def sheets(id):
    course = SchoolCourse.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        file = request.files.get("file")

        if not title or not file or file.filename == "":
            flash("Sheet title and file are required.", "danger")
            return redirect(url_for("school_admin.sheets", id=course.id))

        try:
            file_url = save_sheet_file(file)
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("school_admin.sheets", id=course.id))

        sheet = SchoolSheet(title=title, file_url=file_url, course_id=course.id)
        db.session.add(sheet)
        db.session.commit()
        flash("Sheet uploaded.", "success")
        return redirect(url_for("school_admin.sheets", id=course.id))

    return render_template("admin/school/sheets.html", name="Sheets", course=course)


@school_admin.route("/sheets/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_sheet(id):
    sheet = SchoolSheet.query.get_or_404(id)
    course_id = sheet.course_id
    db.session.delete(sheet)
    db.session.commit()
    flash("Sheet deleted.", "success")
    return redirect(url_for("school_admin.sheets", id=course_id))


#======ASSIGNMENTS=====///
@school_admin.route("/courses/<int:id>/assignments", methods=["GET", "POST"])
@login_required
@admin_required
def assignments(id):
    course = SchoolCourse.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Assignment title is required.", "danger")
            return redirect(url_for("school_admin.assignments", id=course.id))

        assignment = Assignment(title=title, description=description, course_id=course.id)
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment added.", "success")
        return redirect(url_for("school_admin.assignments", id=course.id))

    return render_template("admin/school/assignments.html", name="Assignments", course=course)


@school_admin.route("/assignments/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    course_id = assignment.course_id
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("school_admin.assignments", id=course_id))


#======QUESTIONS=====///
@school_admin.route("/assignment/<int:id>/questions", methods=["GET", "POST"])
@login_required
@admin_required
def questions(id):
    assignment = Assignment.query.get_or_404(id)

    if request.method == "POST":
        question_text = request.form.get("question_text", "").strip()
        question_type = request.form.get("question_type", "mcq")
        correct_answer = request.form.get("correct_answer", "").strip()
        options_raw = request.form.getlist("option")
        options = "||".join([o.strip() for o in options_raw if o.strip()]) if question_type == "mcq" else None

        if not question_text or not correct_answer:
            flash("Question text and correct answer are required.", "danger")
            return redirect(url_for("school_admin.questions", id=assignment.id))

        question = Question(
            question_text=question_text,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            assignment_id=assignment.id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added.", "success")
        return redirect(url_for("school_admin.questions", id=assignment.id))

    return render_template("admin/school/questions.html", name="Questions", assignment=assignment)


@school_admin.route("/questions/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    assignment_id = question.assignment_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted.", "success")
    return redirect(url_for("school_admin.questions", id=assignment_id))
