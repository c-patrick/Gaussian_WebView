from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user

from app.edit import bp
from app.extensions import db, make_decimal
from app.models.qc_data import QC_data


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # UPDATE RECORD
        new_data = {}
        data_id = request.form["id"]
        data_to_update = db.get_or_404(QC_data, data_id)
        form_data = request.form.to_dict()
        print(form_data)
        for key, value in form_data.items():
            if value != "":
                new_data[key] = value
        # Convert to correct data type for database
        make_decimal(new_data)
        # Write updated values to database
        for key, value in new_data.items():
            setattr(data_to_update, key, value)
        db.session.commit()
        db.session.flush()
        return redirect(url_for("main.index"))
    if current_user.is_authenticated:
        data_id = request.args.get("id")
        data_selected = db.get_or_404(QC_data, data_id)
        return render_template("edit.html", data=data_selected)
    else:
        flash("Please authenticate to edit data.")
        return redirect(url_for("login.index"))
