# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return "Accès refusé", 403
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/kyc")
@login_required
@admin_required
def kyc_list():
    users = User.query.filter(User.verification_status == "pending").all()
    return render_template("admin_kyc_list.html", users=users)


@admin_bp.route("/kyc/<int:user_id>/validate", methods=["POST"])
@login_required
@admin_required
def kyc_validate(user_id):
    user = User.query.get_or_404(user_id)
    status = request.form.get("status", "pending")
    notes = request.form.get("notes", "")

    user.verification_status = status
    user.verification_notes = notes
    db.session.commit()

    flash("Statut de vérification mis à jour.", "success")
    return redirect(url_for("admin.kyc_list"))
