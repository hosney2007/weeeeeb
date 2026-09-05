#imports======================///
from flask import Blueprint, render_template,redirect,request,url_for,flash,current_app,abort
from models.recorded import Recorded
from flask_login import login_required,current_user
from extinsion import db
from models.lesson import Lessons
from models.purchase import Purchase
from models.recorded_sheet import RecordedSheet
from models.recorded_assignment import RecordedAssignment
from models.recorded_question import RecordedQuestion
from models.recorded_submission import RecordedSubmission
from utils.decorators import admin_required, save_sheet_file
from utils.uploads import upload_course_image

recorded = Blueprint("recorded",__name__)

#============[RECORDED PAGE]====////
@recorded.route("/courses/recorded", methods=["POST", "GET"])
def recorded_page():
    recorded = Recorded.query.all()
    purchases ={}
    if current_user.is_authenticated:
        user_purchases = Purchase.query.filter_by(user_id=current_user.id).all()
        purchases ={purchase.recorded_course_id: purchase
                   for purchase in user_purchases
                   }
    return render_template("recorded.html", recorded=recorded ,purchases=purchases)

#=======RECORDED COURSES=====//
@recorded.route("/admin/recorded", methods=["POST", "GET"])
@login_required
@admin_required
def recorded_courses(): 
    recorded = Recorded.query.all()
    return render_template("admin/recorded.html" ,recorded=recorded , name= "recorded")

#========ADD COURSE====///
@recorded.route("/admin/recorded/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_course():

    if request.method == "POST":
        thumbnail = request.files.get("thumbnail")
        image_url = upload_course_image(thumbnail, "recorded_courses")

        title = request.form.get("title")
        description = request.form.get("description")

        price_raw = request.form.get("price", "").strip()
        try:
            price = float(price_raw) if price_raw else None
            if price is not None and price < 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid price.", "danger")
            return redirect(url_for("recorded.add_course"))

        new_recorded = Recorded(
            title = title,
            description= description,
            price=price,
            thumbnail=image_url
        )  
        db.session.add(new_recorded)
        db.session.commit()
        flash("recorded course added successfuly ")
        return redirect(url_for("recorded.recorded_courses"))
    return render_template("admin/add-recorded.html" , name="add Course") 

#=======EDIT=====//
@recorded.route("/admin/recorded/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_course( id ):

    recorded = Recorded.query.get_or_404(id)
    if request.method == "POST":

        price_raw = request.form.get("price", "").strip()
        try:
            price = float(price_raw) if price_raw else None
            if price is not None and price < 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid price.", "danger")
            return redirect(url_for("recorded.edit_course", id=id))

        recorded.title = request.form.get("title")
        recorded.description = request.form.get("description")
        recorded.price = price
        db.session.commit()
        flash("recorded course updated successfully")
        return redirect(url_for("recorded.recorded_courses"))
    return render_template("admin/edit-recorded.html", recorded=recorded, name="Edit Course") 

#====DELETE=====////
@recorded.route("/admin/recorded/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_course( id ):

    recorded = Recorded.query.get_or_404(id)
    if recorded.purchase:
        flash("you can't delete this course because it has orders","danger")
        return redirect(url_for("recorded.recorded_courses"))    
    db.session.delete(recorded)
    db.session.commit()
    return redirect(url_for("recorded.recorded_courses"))
#===============================LESSONS=====================================================///

#==========LESSON VIEW====///
@recorded.route("/admin/recorded/<int:id>/lesson", methods=["POST", "GET"])
@login_required
@admin_required
def lessons(id):  
    recorded_course = Recorded.query.get_or_404(id)

    if request.method == "POST":
        order_raw = request.form.get("lesson_order", "").strip()
        try:
            lesson_order = int(order_raw) if order_raw else len(recorded_course.lessons) + 1
        except ValueError:
            flash("Lesson order must be a whole number.", "danger")
            return redirect(url_for("recorded.lessons", id=recorded_course.id))

        title = request.form.get("title", "").strip()
        video_links = request.form.get("video_links", "").strip()
        if not title or not video_links:
            flash("Lesson title and video link are required.", "danger")
            return redirect(url_for("recorded.lessons", id=recorded_course.id))

        lesson = Lessons(
            title=title,
            video_links=video_links,
            lesson_order=lesson_order,
            recorded_course_id=recorded_course.id
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Lesson added.", "success")
        return redirect(url_for("recorded.lessons", id=recorded_course.id))

    lessons = Lessons.query.filter_by(
        recorded_course_id=id
    ).order_by(Lessons.lesson_order).all()
    return render_template("admin/lessons.html" ,recorded=recorded_course ,lesson=lessons ,name= "recorded")
#======ADD LESSON====///

@recorded.route("/admin/recorded/<int:id>/lesson/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_lesson(id):
    recorded = Recorded.query.get_or_404(id)
    if request.method == "POST":
        order_raw = request.form.get("lesson_order", "").strip()
        try:
            lesson_order = int(order_raw) if order_raw else None
        except ValueError:
            flash("Lesson order must be a whole number.", "danger")
            return redirect(url_for("recorded.add_lesson", id=recorded.id))

        title = request.form.get("title", "").strip()
        video_links = request.form.get("video_links", "").strip()
        if not title or not video_links:
            flash("Lesson title and video link are required.", "danger")
            return redirect(url_for("recorded.add_lesson", id=recorded.id))

        lesson=Lessons(
          title = title,
          video_links = video_links,
          lesson_order = lesson_order,
          recorded_course_id=recorded.id
        )
        db.session.add(lesson)
        db.session.commit()
        return redirect(url_for("recorded.lessons", id=recorded.id))
    return render_template("admin/add-lesson.html", recorded=recorded ,name="add lesson")   

#=======EDIT LESSON=======///
@recorded.route("/admin/lesson/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_lesson( id ):

    lesson = Lessons.query.get_or_404(id)
    if request.method == "POST":
        order_raw = request.form.get("lesson_order", "").strip()
        try:
            lesson_order = int(order_raw) if order_raw else None
        except ValueError:
            flash("Lesson order must be a whole number.", "danger")
            return redirect(url_for("recorded.edit_lesson", id=id))

        lesson.title = request.form.get("title", "").strip()
        lesson.video_links = request.form.get("video_links", "").strip()
        lesson.lesson_order = lesson_order

        db.session.commit()
        flash("recorded course updated successfully")
        return redirect(url_for("recorded.lessons", id=lesson.recorded_course_id))
    return render_template("admin/edit-lesson.html", lesson=lesson, name="Edit lesson") 

#==============DELETE LESSON======///
@recorded.route("/admin/lesson/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_lesson( id ):

    lesson = Lessons.query.get_or_404(id)

    db.session.delete(lesson)
    db.session.commit()
    return redirect(url_for("recorded.lessons",id = lesson.recorded_course_id ))
#===============================SHEETS=====================================================///

#==========SHEETS VIEW/ADD====///
@recorded.route("/admin/recorded/<int:id>/sheets", methods=["GET", "POST"])
@login_required
@admin_required
def sheets(id):
    recorded_course = Recorded.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        file = request.files.get("file")

        if not title or not file or file.filename == "":
            flash("Sheet title and file are required.", "danger")
            return redirect(url_for("recorded.sheets", id=recorded_course.id))

        try:
            file_url = save_sheet_file(file, folder="recorded_sheets")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("recorded.sheets", id=recorded_course.id))

        sheet = RecordedSheet(title=title, file_url=file_url, recorded_course_id=recorded_course.id)
        db.session.add(sheet)
        db.session.commit()
        flash("Sheet uploaded.", "success")
        return redirect(url_for("recorded.sheets", id=recorded_course.id))

    return render_template("admin/recorded/sheets.html", name="Sheets", recorded=recorded_course)

#==========DELETE SHEET====///
@recorded.route("/admin/recorded/sheets/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_sheet(id):
    sheet = RecordedSheet.query.get_or_404(id)
    course_id = sheet.recorded_course_id
    db.session.delete(sheet)
    db.session.commit()
    flash("Sheet deleted.", "success")
    return redirect(url_for("recorded.sheets", id=course_id))

#===============================ASSIGNMENTS=====================================================///

#==========ASSIGNMENTS VIEW/ADD====///
@recorded.route("/admin/recorded/<int:id>/assignments", methods=["GET", "POST"])
@login_required
@admin_required
def assignments(id):
    recorded_course = Recorded.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Assignment title is required.", "danger")
            return redirect(url_for("recorded.assignments", id=recorded_course.id))

        assignment = RecordedAssignment(title=title, description=description, recorded_course_id=recorded_course.id)
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment added.", "success")
        return redirect(url_for("recorded.assignments", id=recorded_course.id))

    return render_template("admin/recorded/assignments.html", name="Assignments", recorded=recorded_course)

#==========DELETE ASSIGNMENT====///
@recorded.route("/admin/recorded/assignments/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_assignment(id):
    assignment = RecordedAssignment.query.get_or_404(id)
    course_id = assignment.recorded_course_id
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("recorded.assignments", id=course_id))

#===============================QUESTIONS=====================================================///

#==========QUESTIONS VIEW/ADD====///
@recorded.route("/admin/recorded/assignment/<int:id>/questions", methods=["GET", "POST"])
@login_required
@admin_required
def questions(id):
    assignment = RecordedAssignment.query.get_or_404(id)

    if request.method == "POST":
        question_text = request.form.get("question_text", "").strip()
        question_type = request.form.get("question_type", "mcq")
        correct_answer = request.form.get("correct_answer", "").strip()
        options_raw = request.form.getlist("option")
        options = "||".join([o.strip() for o in options_raw if o.strip()]) if question_type == "mcq" else None

        if not question_text or not correct_answer:
            flash("Question text and correct answer are required.", "danger")
            return redirect(url_for("recorded.questions", id=assignment.id))

        question = RecordedQuestion(
            question_text=question_text,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            assignment_id=assignment.id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added.", "success")
        return redirect(url_for("recorded.questions", id=assignment.id))

    return render_template("admin/recorded/questions.html", name="Questions", assignment=assignment)

#==========DELETE QUESTION====///
@recorded.route("/admin/recorded/questions/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_question(id):
    question = RecordedQuestion.query.get_or_404(id)
    assignment_id = question.assignment_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted.", "success")
    return redirect(url_for("recorded.questions", id=assignment_id))

#==========================================PAYMENTS=======================================================////

#=======BUY=====///

#=================ORDERS======================////
@recorded.route("/admin/orders", methods=["GET", "POST"])
@login_required
@admin_required
def orders():
    orders = Purchase.query.order_by(Purchase.id.desc()).all()
    return render_template("admin/orders.html", orders=orders)

#====== APPROVE ORDERS======///
@recorded.route("/admin/orders/<int:id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_order(id):
    order = Purchase.query.get_or_404(id)
    order.status = "approved"
    db.session.commit()
    return redirect(url_for("recorded.orders"))

#==========REJECT ORDERS====///
@recorded.route("/admin/orders/<int:id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_order(id):
    order = Purchase.query.get_or_404(id)
    order.status = "rejected"
    db.session.commit()
    return redirect(url_for("recorded.orders"))

#==============DELETE order======///
@recorded.route("/admin/orders/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_order( id ):

    order = Purchase.query.get_or_404(id)

    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("recorded.orders"))

# Backward-compatible purchase link used by the recorded-courses template.
@recorded.route("/courses/recorded/<int:id>/buy")
@login_required
def buy_course(id):
    return redirect(url_for("recorded.payment", id=id))

#==========PAYMENTS PAGE=====///
@recorded.route("/courses/recorded/<int:id>/payment", methods=["GET", "POST"])
@login_required
def payment(id):
    # الكورس
    recorded = Recorded.query.get_or_404(id)

    # عملية الشراء الخاصة بالمستخدم
    purchase = Purchase.query.filter_by(
        user_id=current_user.id,
        recorded_course_id=id
    ).first()
    
    # رفع الصورة
    if request.method == "POST":

        image = request.files.get("payment_image")
        notes = request.form.get("notes", "").strip()

        if image and image.filename != "":
            if purchase is None:
              purchase = Purchase(
              user_id=current_user.id,
              recorded_course_id=id,
              status="pending"
            )
   
            db.session.add(purchase)

            image_url = upload_course_image(image, "payments")
            purchase.payment_image = image_url
            purchase.notes = notes or None
            purchase.status = "waiting"

            db.session.commit()

            flash("Payment uploaded successfully.", "success")

            return redirect(url_for("recorded.recorded_page"))

        flash("Please choose an image.", "danger")

    return render_template(
        "payment.html",
        recorded=recorded,
        purchase=purchase,
        name=recorded.title,
        vodafone_cash_number=current_app.config["VODAFONE_CASH_NUMBER"],
        instapay_id=current_app.config["INSTAPAY_ID"]
    )

#==========STUDENT LESSON PAGE=======///

@recorded.route("/recorded/<int:course_id>/lessons")
@login_required
def course_lessons(course_id):

    recorded = Recorded.query.get_or_404(course_id)

    purchase = Purchase.query.filter_by(
        user_id=current_user.id,
        recorded_course_id=course_id
    ).first()

    if not purchase:
        flash("You must purchase this course first.", "danger")
        return redirect(url_for("recorded.payment", id=course_id))

    if purchase.status != "approved":
        flash("Your payment is still under review.", "warning")
        return redirect(url_for("recorded.recorded_page"))

    lessons = Lessons.query.filter_by(
        recorded_course_id=course_id
    ).order_by(Lessons.lesson_order).all()

    if not lessons:
        flash("No lessons available.", "warning")
        return redirect(url_for("recorded.recorded_page"))

    lesson_id = request.args.get("lesson", type=int)

    if lesson_id:
        lesson = Lessons.query.filter_by(
            id=lesson_id,
            recorded_course_id=course_id
        ).first_or_404()
    else:
        lesson = lessons[0]

    return render_template(
        "lessons.html",
        recorded=recorded,
        lesson=lesson,
        lessons=lessons,
        name=recorded.title
    )

#==========================================PURCHASER SHEETS & ASSIGNMENTS==================================////

def _approved_purchase_or_redirect(course_id):
    """Returns (purchase, None) if the current user has an approved purchase for
    this recorded course, otherwise (None, redirect_response)."""
    purchase = Purchase.query.filter_by(
        user_id=current_user.id,
        recorded_course_id=course_id
    ).first()

    if not purchase:
        flash("You must purchase this course first.", "danger")
        return None, redirect(url_for("recorded.payment", id=course_id))

    if purchase.status != "approved":
        flash("Your payment is still under review.", "warning")
        return None, redirect(url_for("recorded.recorded_page"))

    return purchase, None

#==========COURSE HOME (lessons + sheets + assignments hub)=======///
@recorded.route("/recorded/<int:course_id>")
@login_required
def course_home(course_id):
    recorded_course = Recorded.query.get_or_404(course_id)

    _, blocked = _approved_purchase_or_redirect(course_id)
    if blocked:
        return blocked

    lessons = Lessons.query.filter_by(
        recorded_course_id=course_id
    ).order_by(Lessons.lesson_order).all()

    submissions = {
        s.assignment_id: s for s in RecordedSubmission.query.filter_by(
            student_id=current_user.id
        ).all()
    }

    return render_template(
        "recorded/course.html",
        recorded=recorded_course,
        lessons=lessons,
        submissions=submissions,
        name=recorded_course.title
    )

#==========STUDENT SHEETS=======///
@recorded.route("/recorded/<int:course_id>/sheets")
@login_required
def student_sheets(course_id):
    recorded_course = Recorded.query.get_or_404(course_id)

    _, blocked = _approved_purchase_or_redirect(course_id)
    if blocked:
        return blocked

    return render_template(
        "recorded/sheets.html",
        recorded=recorded_course,
        sheets=recorded_course.sheets,
        name=recorded_course.title
    )

#==========STUDENT ASSIGNMENTS=======///
@recorded.route("/recorded/<int:course_id>/assignments")
@login_required
def student_assignments(course_id):
    recorded_course = Recorded.query.get_or_404(course_id)

    _, blocked = _approved_purchase_or_redirect(course_id)
    if blocked:
        return blocked

    submissions = {
        s.assignment_id: s for s in RecordedSubmission.query.filter_by(
            student_id=current_user.id
        ).all()
    }

    return render_template(
        "recorded/assignments.html",
        recorded=recorded_course,
        assignments=recorded_course.assignments,
        submissions=submissions,
        name=recorded_course.title
    )

#==========TAKE ASSIGNMENT=======///
@recorded.route("/recorded/assignment/<int:id>")
@login_required
def take_assignment(id):
    assignment = RecordedAssignment.query.get_or_404(id)

    _, blocked = _approved_purchase_or_redirect(assignment.recorded_course_id)
    if blocked:
        return blocked

    existing = RecordedSubmission.query.filter_by(
        student_id=current_user.id, assignment_id=id
    ).first()

    if existing:
        return redirect(url_for("recorded.assignment_result", id=existing.id))

    return render_template(
        "recorded/assignment.html",
        assignment=assignment,
        name=assignment.title
    )

#==========SUBMIT ASSIGNMENT=======///
@recorded.route("/recorded/assignment/<int:id>/submit", methods=["POST"])
@login_required
def submit_assignment(id):
    assignment = RecordedAssignment.query.get_or_404(id)

    _, blocked = _approved_purchase_or_redirect(assignment.recorded_course_id)
    if blocked:
        return blocked

    existing = RecordedSubmission.query.filter_by(
        student_id=current_user.id, assignment_id=id
    ).first()
    if existing:
        flash("You already submitted this assignment.", "warning")
        return redirect(url_for("recorded.assignment_result", id=existing.id))

    questions = assignment.questions
    correct_count = 0

    for question in questions:
        answer = request.form.get(f"question_{question.id}", "").strip()
        if answer.lower() == (question.correct_answer or "").strip().lower():
            correct_count += 1

    total = len(questions)
    score = round((correct_count / total) * 100, 2) if total else 0

    submission = RecordedSubmission(
        student_id=current_user.id,
        assignment_id=id,
        score=score,
        total=total
    )
    db.session.add(submission)
    db.session.commit()

    flash("Assignment submitted successfully.", "success")
    return redirect(url_for("recorded.assignment_result", id=submission.id))

#==========ASSIGNMENT RESULT=======///
@recorded.route("/recorded/assignment/result/<int:id>")
@login_required
def assignment_result(id):
    submission = RecordedSubmission.query.get_or_404(id)
    if submission.student_id != current_user.id:
        abort(403)
    return render_template(
        "recorded/result.html",
        name="Result",
        submission=submission
    )
