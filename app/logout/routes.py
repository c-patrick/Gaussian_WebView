from flask import redirect, url_for
from flask_login import login_required, logout_user

from app.logout import bp


@bp.route("/")
@login_required
def index():
    logout_user()
    return redirect(url_for("main.index"))
