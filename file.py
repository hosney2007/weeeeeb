#imoprts===============================///
from dotenv import load_dotenv
load_dotenv()
from flask import Flask , render_template, redirect,request,url_for,flash
from config import Config
from flask_login import current_user
from models.user import User
from routes.auth import auth
from routes.courses import course
from routes.scheddules import schedule
from routes.recorded import recorded
from routes.booking import booking
from routes.contact import message
from models.schedaule import Schedule
from models.booking import Booking
from models.message import Message
from models.success_story import SuccessStory
from models.branch import Branch
from routes.admin import admin
from routes.school import school
from routes.admin_school import school_admin
from routes.book import book, BOOK
from models.book_purchase import BookPurchase
from models.grade import Grade
from models.school_course import SchoolCourse
from models.school_lesson import SchoolLesson
from models.school_sheet import SchoolSheet
from models.assignment import Assignment
from models.question import Question
from models.submission import Submission
from models.submission_answer import SubmissionAnswer
from models.recorded_assignment import RecordedAssignment
from models.recorded_sheet import RecordedSheet
from models.recorded_question import RecordedQuestion
from models.recorded_submission import RecordedSubmission
from models.recorded_submission_answer import RecordedSubmissionAnswer
from models.notification import Notification
from routes.notifications import notifications
from utils.notifications import notify_admin
from utils.validators import is_valid_phone, clean_phone
from extinsion import db, login_manager, mail,csrf,limiter
import click
from werkzeug.security import generate_password_hash
from models.course import Course
import os
import logging
from logging.handlers import RotatingFileHandler


app = Flask(__name__, template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"]=True


if not app.debug:
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, "app.log"), maxBytes=1_000_000, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    ))
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.ERROR)


#bluebrint regisrtion====================================///
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(course)
app.register_blueprint(booking)
app.register_blueprint(schedule)
app.register_blueprint(recorded)
app.register_blueprint(message)
app.register_blueprint(school)
app.register_blueprint(school_admin)
app.register_blueprint(book)
app.register_blueprint(notifications)

@app.context_processor
def inject_unread_notifications_count():
    if current_user.is_authenticated:
        count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()
    else:
        count = 0
    return dict(unread_notifications_count=count)

#admin accuont===========================================///

@app.cli.command("create-admin")
@click.option("--name", prompt="admin name")
@click.option("--email", prompt="admin email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin(name,email,password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("Email already registered.")
        return
    admin = User(
         name=name,
         email=email,
         password=generate_password_hash(password),
         role="admin",
         is_verified = True
     )
    db.session.add(admin)
    db.session.commit()
    print("Admin account crated successfuly")


#app configrtion==//
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db.init_app(app)
csrf.init_app(app)
mail.init_app(app)
limiter.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

    
with app.app_context():
    db.create_all()
    from sqlalchemy import inspect, text
    from sqlalchemy.exc import OperationalError, ProgrammingError
    inspector = inspect(db.engine)


    quote = db.engine.dialect.identifier_preparer.quote

    def q(name):
        return quote(name)

    if inspector.has_table("user") and inspector.has_table("grade"):
        existing_columns = {c["name"] for c in inspector.get_columns("user")}
        if "grade_id" not in existing_columns:
            db.session.execute(
                text(f'ALTER TABLE {q("user")} ADD COLUMN grade_id INTEGER REFERENCES {q("grade")}(id)')
            )
            db.session.commit()


    if inspector.has_table("user"):
        user_columns = {c["name"] for c in inspector.get_columns("user")}
        if "phone" not in user_columns:
            db.session.execute(
                text(f'ALTER TABLE {q("user")} ADD COLUMN {q("phone")} VARCHAR(20)')
            )
            db.session.commit()

    if inspector.has_table("bookings") and inspector.has_table("user"):
        booking_columns = {c["name"] for c in inspector.get_columns("bookings")}
        if "user_id" not in booking_columns:
            db.session.execute(
                text(f'ALTER TABLE {q("bookings")} ADD COLUMN user_id INTEGER REFERENCES {q("user")}(id)')
            )
            db.session.commit()


    if inspector.has_table("purchase"):
        purchase_columns = {c["name"] for c in inspector.get_columns("purchase")}
        if "notes" not in purchase_columns:
            db.session.execute(
                text(f'ALTER TABLE {q("purchase")} ADD COLUMN notes TEXT')
            )
            db.session.commit()


    if inspector.has_table("book_purchase"):
        book_purchase_columns = {c["name"] for c in inspector.get_columns("book_purchase")}
        for column_name in ("recipient_name", "phone", "address"):
            if column_name not in book_purchase_columns:
                db.session.execute(
                    text(f'ALTER TABLE {q("book_purchase")} ADD COLUMN {q(column_name)} TEXT')
                )
        db.session.commit()


    fk_indexes = [
        ("assignment", "course_id"),
        ("bookings", "user_id"),
        ("bookings", "course_id"),
        ("bookings", "schedule_id"),
        ("bookings", "branch_id"),
        ("lessons", "recorded_course_id"),
        ("purchase", "user_id"),
        ("purchase", "recorded_course_id"),
        ("question", "assignment_id"),
        ("schedule", "course_id"),
        ("schedule", "branch_id"),
        ("school_course", "grade_id"),
        ("school_lesson", "course_id"),
        ("school_sheet", "course_id"),
        ("submission", "student_id"),
        ("submission", "assignment_id"),
        ("user", "grade_id"),
    ]
    for table_name, column_name in fk_indexes:
        if not inspector.has_table(table_name):
            continue
        index_name = f"ix_{table_name}_{column_name}"
        existing_indexes = {ix["name"] for ix in inspector.get_indexes(table_name)}
        if index_name in existing_indexes:
            continue
        try:
            db.session.execute(
                text(f'CREATE INDEX {q(index_name)} ON {q(table_name)} ({q(column_name)})')
            )
            db.session.commit()
        except (OperationalError, ProgrammingError):

            db.session.rollback()


#main pages routes===================///

@app.route('/')
def home():
    stories = SuccessStory.query.filter_by(
        is_active=True
    ).order_by(
        SuccessStory.id.desc()
    ).limit(6).all()

    book_purchase = None
    if current_user.is_authenticated:
        book_purchase = BookPurchase.query.filter_by(
            user_id=current_user.id
        ).first()

    return render_template(
        'index.html',
        name = 'Home',
        stories=stories,
        book=BOOK,
        book_purchase=book_purchase
    )

@app.route("/about")
def about():
    return render_template('about.html', name = 'ABOUT')    


@app.route("/courses")
def curses():
    return render_template('courses.html', name = 'courses')    

@app.route("/free")
def free_session():
    return render_template('free-session.html', name = 'free')   


@app.route("/booking", methods=["POST", "GET"])
@limiter.limit("5 per minute", methods=["POST"])
def booking():
    if request.method == "POST":
         phone = clean_phone(request.form["student_number"])
         parent_phone = clean_phone(request.form["parent_number"])

         if not is_valid_phone(phone):
             flash("Please enter a valid student phone number (e.g. 01012345678).", "danger")
             return redirect(url_for("booking"))

         if not is_valid_phone(parent_phone):
             flash("Please enter a valid parent phone number (e.g. 01012345678).", "danger")
             return redirect(url_for("booking"))

         schedule = Schedule.query.get_or_404(
             request.form["schedule_id"]
         )
         existing_booking = Booking.query.filter_by(
             schedule_id=schedule.id,
            student_number = phone
         ).first()
         if existing_booking:
             flash("You Have Already Booked this Group", "warning")
             return redirect(url_for("booking"))

         mode = request.form["mode"]
         branch_id = request.form.get("branch_id") or None
         if mode == "online":
             branch_id = None

         booking=Booking(
          user_id = current_user.id if current_user.is_authenticated else None,
          student_name = request.form["student_name"],
          student_number = phone,
          parent_number = parent_phone,
          grade = request.form["grade"],
          mode = mode,
          addational_notes= request.form["addational_notes"],
          course_id = request.form["exam"],
          branch_id = branch_id,
          schedule_id = request.form["schedule_id"],
         )
         db.session.add(booking)
         db.session.commit()

         notify_admin(
             subject=f"New booking: {booking.course.title if booking.course else 'a course'}",
             lines=[
                 f"Student: {request.form['student_name']} ({phone})",
                 f"Parent: {parent_phone}",
                 f"Grade: {request.form['grade']}",
                 f"Mode: {mode}",
                 f"Notes: {request.form.get('addational_notes') or '-'}",
                 f"Review it here: {url_for('booking.admin_booking', _external=True)}",
             ]
         )

         flash("your booking has been confirmed")
         return redirect(url_for("booking"))  
    courses = Course.query.all()
    branches = Branch.query.all()
    return render_template('booking.html', name = 'booking', course=courses, branches=branches )   


@app.route("/contact", methods=["POST", "GET"])
@limiter.limit("5 per minute", methods=["POST"])
def contact():
    if request.method == "POST":
         contact_number = clean_phone(request.form["number"])
         if not is_valid_phone(contact_number):
             flash("Please enter a valid phone number (e.g. 01012345678).", "danger")
             return redirect(url_for("contact"))

         message=Message(
          name = request.form["name"],
          number = contact_number,
          message= request.form["message"],
          course = request.form["course"],
         )
         db.session.add(message)
         db.session.commit()
         flash("your message has been confirmed")
         return redirect(url_for("contact"))  
    return render_template('contact.html', name = 'contact')    

#error handlers===================///
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html", name="Forbidden"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", name="Not Found"), 404

@app.errorhandler(413)
def file_too_large(e):
    return render_template("413.html", name="File Too Large"), 413

@app.errorhandler(500)
def server_error(e):
    app.logger.error("Unhandled server error: %s", e, exc_info=True)
    return render_template("500.html", name="Server Error"), 500

@app.errorhandler(429)
def not_found(e):
    return render_template("429.html", name="too many attempts"), 429


#app run==============///
if __name__ == '__main__':
    app.run(debug=True ,host="0.0.0.0" ,port=9000)