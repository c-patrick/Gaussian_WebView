from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash
import datetime

from app.register import bp
from app.extensions import db
from app.models.user import User


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user:
            # If user exists
            flash("You've already signed up with that email. Try logging in.")
            return redirect(url_for("login.index"))

        hashed_salted_password = generate_password_hash(
            request.form.get("password"), method="pbkdf2:sha256", salt_length=8
        )
        new_user = User(
            email=request.form.get("email"),
            password=hashed_salted_password,
            name=request.form.get("name"),
            email_confirmed_at=datetime.datetime.now(),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("main.index"))

    return render_template("register.html", logged_in=current_user.is_authenticated)
