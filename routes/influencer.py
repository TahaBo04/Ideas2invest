from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models.collaboration import CollaborationRequest

influencer_bp = Blueprint("influencer", __name__, url_prefix="/influencer")


@influencer_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "influencer":
        return "Access denied", 403
    if current_user.creator_profile is None:
        flash("Finish your creator profile to unlock campaign matching.", "info")
        return redirect(url_for("creators.onboarding"))

    requests = (
        CollaborationRequest.query.filter_by(creator_profile_id=current_user.creator_profile.id)
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )
    return render_template("influencer_dashboard.html", requests=requests)
