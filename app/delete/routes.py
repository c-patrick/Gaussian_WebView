from flask import redirect, url_for, request

from app.delete import bp
from app.extensions import db
from app.models.qc_data import QC_data


@bp.route("/")
def index():
    data_id = request.args.get("id")
    # DELETE A RECORD BY ID
    data_to_delete = db.get_or_404(QC_data, data_id)
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(data_to_delete)
    db.session.commit()
    return redirect(url_for("main.index"))
