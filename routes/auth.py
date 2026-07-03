from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User
from services.logging_service import log_login

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form.get("role", "influencer")

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        id_type = request.form.get("id_type", "").strip()
        id_number = request.form.get("id_number", "").strip()

        if not email or not password or not first_name or not last_name:
            flash("Please complete all required fields.", "danger")
            return redirect(url_for("auth.register"))

        if role not in ("influencer", "business"):
            flash("Choose whether you are joining as an influencer or a business.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("This email is already in use.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            first_name=first_name,
            last_name=last_name,
            id_type=id_type,
            id_number=id_number,
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created. Your profile is pending verification.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            if user:
                log_login(user, success=False, failure_reason="wrong_password")
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)

        # Update last login only if your model has this column
        if hasattr(user, "last_login_at"):
            user.last_login_at = datetime.utcnow()
            db.session.commit()

        log_login(user, success=True)

        if user.role == "business":
            return redirect(url_for("business.dashboard"))
        if user.role == "admin":
            return redirect(url_for("admin.verification_dashboard"))
        return redirect(url_for("influencer.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("home"))
