from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user

from app.edit import bp
from app.extensions import db, make_decimal
from app.models.qc_data import QC_data
from app.models.user import User


@bp.route("/", methods=["GET", "POST"])
def index():
    # Get data type
    if request.method == "POST":
        # UPDATE RECORD
        new_data = {}
        data_id = request.form["id"]
        # If QC_data type
        if "qc_data-submit" in request.form:
            print("YES!")
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
        # If user type
        elif "user-submit" in request.form:
            data_to_update = db.get_or_404(User, data_id)
            form_data = request.form.to_dict()
            print(form_data)
            for key, value in form_data.items():
                if value != "":
                    new_data[key] = value
            # Write updated values to database
            for key, value in new_data.items():
                setattr(data_to_update, key, value)
            db.session.commit()
            db.session.flush()
            return redirect(url_for("users.index"))
    if current_user.is_authenticated:
        data_id = request.args["id"]
        data_type = request.args["type"]
        if data_type == "qc_data":
            data_selected = db.get_or_404(QC_data, data_id)
        elif data_type == "user":
            data_selected = db.get_or_404(User, data_id)
        return render_template("edit.html", data_type=data_type, data=data_selected)
    else:
        flash("Please authenticate to edit data.")
        return redirect(url_for("login.index"))
