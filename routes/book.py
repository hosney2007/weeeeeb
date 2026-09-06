#imports=============================///
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extinsion import db
from models.book_purchase import BookPurchase
from utils.decorators import admin_required
from utils.uploads import upload_course_image
from utils.notifications import notify_admin, notify_student

book = Blueprint("book", __name__)

# Static book data shown on the homepage "Exclusive Book" section.
# Not admin-managed yet — edit this dict (and the cover text in
# templates/index.html / templates/book_payment.html) to update it.
BOOK = {
    "title": "Digital SAT Math",
    "subtitle": "The Ultimate Guide to Digital SAT Math",
    "description": "Strategies, practice and confidence to master every Digital SAT Math topic — by Mr. Abdelfattah Barakat.",
    "price": 500,
    "delivery_price": 100,
    "features": [
        "Complete Concepts",
        "Smart Strategies",
        "Practice Questions",
        "Maximum Score",
    ],
}


#============[BUY BOOK / PAYMENT PAGE]====////
@book.route("/book/buy", methods=["GET", "POST"])
@login_required
def buy():
    purchase = BookPurchase.query.filter_by(user_id=current_user.id).first()
    total_price = BOOK["price"] + BOOK["delivery_price"]
    form_values = {
        "recipient_name": (purchase.recipient_name if purchase else current_user.name) or "",
        "phone": (purchase.phone if purchase else "") or "",
        "address": (purchase.address if purchase else "") or "",
        "notes": (purchase.notes if purchase else "") or "",
    }

    if request.method == "POST":
        image = request.files.get("payment_image")
        notes = request.form.get("notes", "").strip()
        recipient_name = request.form.get("recipient_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        form_values = {
            "recipient_name": recipient_name,
            "phone": phone,
            "address": address,
            "notes": notes,
        }

        if not recipient_name or not phone or not address:
            flash("Please fill in the recipient name, phone and delivery address.", "danger")
        elif not image or image.filename == "":
            flash("Please choose a payment screenshot.", "danger")
        else:
            if purchase is None:
                purchase = BookPurchase(user_id=current_user.id, status="pending")
                db.session.add(purchase)

            image_url = upload_course_image(image, "book_payments")
            purchase.payment_image = image_url
            purchase.notes = notes or None
            purchase.recipient_name = recipient_name
            purchase.phone = phone
            purchase.address = address
            purchase.status = "waiting"

            db.session.commit()

            notify_admin(
                subject=f"New book order: {BOOK['title']}",
                lines=[
                    f"Buyer: {current_user.name} ({current_user.email})",
                    f"Recipient: {recipient_name}",
                    f"Phone: {phone}",
                    f"Address: {address}",
                    f"Notes: {notes or '-'}",
                    f"Review it here: {url_for('book.admin_orders', _external=True)}",
                ]
            )

            flash("Payment uploaded successfully.", "success")
            return redirect(url_for("home"))

    return render_template(
        "book_payment.html",
        book=BOOK,
        purchase=purchase,
        total_price=total_price,
        form_values=form_values,
        name=BOOK["title"],
        vodafone_cash_number=current_app.config["VODAFONE_CASH_NUMBER"],
        instapay_id=current_app.config["INSTAPAY_ID"],
    )


#==========================================ADMIN: BOOK ORDERS=======================================================////

@book.route("/admin/book-orders")
@login_required
@admin_required
def admin_orders():
    orders = BookPurchase.query.order_by(BookPurchase.id.desc()).all()
    return render_template("admin/book_orders.html", orders=orders, name="Book Orders")


@book.route("/admin/book-orders/<int:id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_order(id):
    order = BookPurchase.query.get_or_404(id)
    order.status = "approved"
    db.session.commit()
    notify_student(
        order.user,
        title="Your book order has been approved",
        message=f"Your order for '{BOOK['title']}' has been approved and is being prepared for delivery.",
        link_endpoint="home"
    )
    return redirect(url_for("book.admin_orders"))


@book.route("/admin/book-orders/<int:id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_order(id):
    order = BookPurchase.query.get_or_404(id)
    order.status = "rejected"
    db.session.commit()
    notify_student(
        order.user,
        title="Your book order needs attention",
        message=f"Your order for '{BOOK['title']}' couldn't be approved. Please check your payment proof and try again.",
        link_endpoint="book.buy"
    )
    return redirect(url_for("book.admin_orders"))


@book.route("/admin/book-orders/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_order(id):
    order = BookPurchase.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("book.admin_orders"))
