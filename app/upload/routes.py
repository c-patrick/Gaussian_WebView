import os
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.upload import bp, allowed_file, process_json


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            error = process_json(file_path)
            if error:
                # If error encountered
                return redirect(url_for("compare.index"))
            else:
                return redirect(url_for("main.index"))
    return render_template("upload.html")
