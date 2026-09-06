#imports=============///
from flask import Blueprint, render_template, request, redirect, url_for,flash,current_app
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from models.booking import Booking
from models.purchase import Purchase
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from extinsion import mail,limiter




from extinsion import db
from models.user import User
from models.grade import Grade
from utils.validators import is_valid_phone, clean_phone

auth = Blueprint("auth" ,__name__)

#email verification=====================///

def generate_verification_token(email):

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    return serializer.dumps(
        email,
        salt="email-confirm"
    )

def send_verification_email(user):

    token = generate_verification_token(user.email)

    verify_url = url_for(
        "auth.verify_email",
        token=token,
        _external=True
    )

    msg = Message(

        subject="Verify your Abdelfatah Academy account",

        recipients=[user.email]

    )

    msg.body = f"""
Hello {user.name},

Thank you for registering at Abdelfatah Academy.

Please click the link below to verify your email:

{verify_url}

If you did not create this account, simply ignore this email.

Regards,
Abdelfatah Academy
"""
    mail.send(msg)

#reset passwoed verify============///
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    return serializer.dumps(
        email,
        salt="password-reset"
    )

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=expiration
        )

        return email

    except (BadSignature, SignatureExpired):
        return None

def send_reset_password_email(user):

    token = generate_reset_token(user.email)

    reset_url = url_for(
        "auth.reset_password",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Reset your Abdelfatah Academy password",
        recipients=[user.email]
    )

    msg.body = f"""
Hello {user.name},

We received a request to reset your password.

Click the link below to create a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Regards,
Abdelfatah Academy
"""

    mail.send(msg)



#=========REGISTER======///
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@auth.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        phone = clean_phone(request.form.get("phone", ""))
        parent_phone = clean_phone(request.form.get("parent_phone", ""))
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password", "")
        grade_code = request.form.get("grade_code", "").strip().upper()

        if len(name) < 3:
            flash("Name must be at least 3 characters.", "danger")
            return redirect(url_for("auth.register"))

        if not EMAIL_REGEX.match(email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("auth.register"))

        if not is_valid_phone(phone):
            flash("Please enter a valid phone number (e.g. 01012345678).", "danger")
            return redirect(url_for("auth.register"))

        if not is_valid_phone(parent_phone):
            flash("Please enter a valid parent's phone number (e.g. 01012345678).", "danger")
            return redirect(url_for("auth.register"))

        if phone == parent_phone:
            flash("Parent's phone number must be different from your own phone number.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered","danger")
            return redirect(url_for("auth.register"))

        role = "student"
        grade_id = None
        if grade_code:
            grade = Grade.query.filter_by(code=grade_code).first()
            if not grade:
                flash("Invalid grade code.", "danger")
                return redirect(url_for("auth.register"))
            role = "school_student"
            grade_id = grade.id

        hashed_password = generate_password_hash(password)
        user = User(
            name=name,
            email=email,
            phone=phone,
            parent_phone=parent_phone,
            password=hashed_password,
            role=role,
            grade_id=grade_id
        )
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash( "Account created successfully! Please check your email to verify your account.","success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", name="Register")

#======verify====///
@auth.route("/verify-email/<token>")
def verify_email(token):

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    try:

        email = serializer.loads(
            token,
            salt="email-confirm",
            max_age=3600
        )

    except SignatureExpired:

        flash("Verification link has expired.", "danger")
        return redirect(url_for("auth.login"))

    except BadSignature:

        flash("Invalid verification link.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if not user:

        flash("Account not found.", "danger")
        return redirect(url_for("auth.login"))

    if user.is_verified:

        flash("Your account is already verified.", "info")
        return redirect(url_for("auth.login"))

    user.is_verified = True

    db.session.commit()

    flash("Your email has been verified successfully. You can now login.", "success")

    return redirect(url_for("auth.login"))

@auth.route("/resend-verification", methods=["POST"])
@limiter.limit("2 per minute")
def resend_verification():

    email = request.form.get("email", "").strip().lower()

    user = User.query.filter_by(email=email).first()

    if not user:

        flash("Account not found.", "danger")

        return redirect(url_for("auth.login"))

    if user.is_verified:

        flash("Your account is already verified.", "info")

        return redirect(url_for("auth.login"))

    send_verification_email(user)

    flash("Verification email sent successfully.", "success")

    return redirect(url_for("auth.login"))

#=========LOGIN========////
@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]   
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash("Please verify your email first.","warning")
                return redirect(url_for("auth.login"))
            login_user(user)
            flash("welcome back!","success")
            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            if user.role == "school_student":
                return redirect(url_for("school.dashboard"))
            return redirect(url_for("auth.dashboard"))
        flash("Invalid email or password","danger")
        return redirect(url_for("auth.login"))
    return render_template("login.html", name="Login", show_resend=True)

#forgot password===========////
@auth.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def forgot_password():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        user = User.query.filter_by(email=email).first()

        if user:
            send_reset_password_email(user)

        flash(
            "If this email exists, a password reset link has been sent.",
            "info"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "forgot_password.html",
        name="Forgot Password"
    )

#reset passworrd=============///
@auth.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def reset_password(token):

    email = verify_reset_token(token)

    if not email:
        flash("This reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == "POST":

        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        user.password = generate_password_hash(password)

        db.session.commit()

        flash("Password changed successfully.", "success")

        return redirect(url_for("auth.login"))

    return render_template(
        "reset_password.html",
        name="Reset Password"
    )


#======DASHBOARD=====///
@auth.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    if current_user.role == "school_student":
        return redirect(url_for("school.dashboard"))

    user = current_user

    purchases = Purchase.query.filter_by(
        user_id=current_user.id,
        status="approved"
    ).all()


    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    total_recorded = len(purchases)
    total_bookings = len(bookings)

    pending_bookings = sum(1 for b in bookings if b.status == "pending")
    approved_bookings = sum(1 for b in bookings if b.status == "approved")

    return render_template(
        "dashboard.html",
        user=user,
        purchases=purchases,
        bookings=bookings,
        total_recorded=total_recorded,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings
    )

#=====LOGOUT==//
@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))            

