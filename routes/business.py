from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.campaign import Campaign
from models.collaboration import CollaborationRequest

business_bp = Blueprint("business", __name__, url_prefix="/business")


@business_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "business":
        return "Access denied", 403

    campaigns = Campaign.query.filter_by(business_id=current_user.id).order_by(Campaign.created_at.desc()).all()
    requests = (
        CollaborationRequest.query.join(Campaign)
        .filter(Campaign.business_id == current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )
    return render_template("business_dashboard.html", campaigns=campaigns, requests=requests)
