# routes/investor.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

investor_bp = Blueprint("investor", __name__, url_prefix="/investor")


@investor_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "investor":
        return "Accès refusé", 403
    return render_template("investor_dashboard.html")
