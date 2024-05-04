from flask import redirect, url_for, request

from app.delete import bp
from app.extensions import db, admin_required
from app.models.qc_data import QC_data
from app.models.user import User


@bp.route("/")
@admin_required
def index():
    data_type = request.args.get("type")
    data_id = request.args.get("id")

    if data_type == "qc_data":
        # DELETE A RECORD BY ID
        data_to_delete = db.get_or_404(QC_data, data_id)
    elif data_type == "user":
        data_to_delete = db.get_or_404(User, data_id)
    db.session.delete(data_to_delete)
    db.session.commit()
    return redirect(url_for("main.index"))
