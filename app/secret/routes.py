from flask import render_template

from app.secret import bp
from app.extensions import admin_required


@bp.route("/")
@admin_required
def index():
    return render_template("secret.html")
