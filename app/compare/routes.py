from flask import render_template, redirect, url_for, request, session
from flask_login import login_required

from app.compare import bp
from app.models.qc_data import QC_data


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        return redirect(url_for("main.index"))
    data_to_add = session["new_data"]
    if data_to_add == {}:
        existing_data = {}
    else:
        existing_data = QC_data.query.filter_by(qc_name=data_to_add["qc_name"]).scalar()
    return render_template(
        "compare.html", existing_data=existing_data, data_to_add=data_to_add
    )
