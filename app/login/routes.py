from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash

from app.login import bp
from app.extensions import db
from app.models.user import User


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            # User does not exist
            flash("That email does not exist, please try again.")
            return redirect(url_for("login.index"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.")
            return redirect(url_for("login.index"))
        else:
            login_user(user)
            return redirect(url_for("main.index"))
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for("main.index"))
    return render_template("login.html")
