from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return "Access denied", 403
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/verification")
@login_required
@admin_required
def verification_dashboard():
    users = User.query.filter(User.verification_status == "pending").all()
    return render_template("admin_verification.html", users=users)


@admin_bp.route("/verification/<int:user_id>/validate", methods=["POST"])
@login_required
@admin_required
def verification_validate(user_id):
    user = User.query.get_or_404(user_id)
    status = request.form.get("status", "pending")
    notes = request.form.get("notes", "")

    user.verification_status = status
    user.verification_notes = notes
    db.session.commit()

    flash("Verification status updated.", "success")
    return redirect(url_for("admin.verification_dashboard"))
