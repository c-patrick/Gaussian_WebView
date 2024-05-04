from flask import render_template
from flask_login import login_required, logout_user
from app.extensions import db, admin_required
from app.models.user import User

from app.users import bp


@bp.route("/")
@admin_required
def index():
    result = db.session.execute(db.select(User).order_by(User.id))
    all_data = result.scalars()
    return render_template("users.html", data=all_data)
