# routes/profile.py
from __future__ import annotations

import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models.user import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_upload_dir() -> str:
    """Return a writable upload directory.  On Vercel the project tree is
    read-only so we fall back to /tmp."""
    if os.environ.get("VERCEL"):
        d = "/tmp/uploads/profile_pics"
    else:
        d = os.path.join(current_app.root_path, "static", "uploads", "profile_pics")
    os.makedirs(d, exist_ok=True)
    return d


def _remove_old_picture(filename: str | None) -> None:
    if not filename:
        return
    upload_dir = _get_upload_dir()
    old_path = os.path.join(upload_dir, filename)
    if os.path.isfile(old_path):
        os.remove(old_path)


@profile_bp.route("/<int:user_id>")
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("profile_public.html", profile_user=user)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.first_name = request.form.get("first_name", current_user.first_name).strip()
        current_user.last_name = request.form.get("last_name", current_user.last_name).strip()
        current_user.bio = request.form.get("bio", "").strip()

        # Handle profile picture upload
        pic = request.files.get("profile_picture")
        if pic and pic.filename and _allowed_file(pic.filename):
            ext = secure_filename(pic.filename).rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            upload_dir = _get_upload_dir()
            _remove_old_picture(current_user.profile_picture)
            pic.save(os.path.join(upload_dir, filename))
            current_user.profile_picture = filename

        db.session.commit()
        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for("profile.public_profile", user_id=current_user.id))

    return render_template("profile_edit.html")
