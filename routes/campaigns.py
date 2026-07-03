from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.campaign import Campaign
from models.collaboration import CollaborationRequest
from models.creator import CreatorProfile
from services.matching_service import calculate_match_score, score_creators_for_campaign
from services.security_service import is_business, is_influencer

campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")


@campaigns_bp.route("/")
def list_campaigns():
    campaigns = Campaign.query.filter_by(status="open").order_by(Campaign.created_at.desc()).all()
    profile = current_user.creator_profile if current_user.is_authenticated and current_user.role == "influencer" else None
    scores = {}
    if profile:
        scores = {campaign.id: calculate_match_score(campaign, profile) for campaign in campaigns}
    return render_template("campaigns_list.html", campaigns=campaigns, scores=scores)


@campaigns_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_campaign():
    if not is_business():
        flash("Only business accounts can post campaign briefs.", "danger")
        return redirect(url_for("campaigns.list_campaigns"))

    if request.method == "POST":
        campaign = Campaign(
            business_id=current_user.id,
            title=request.form.get("title", "").strip(),
            industry=request.form.get("industry", "").strip(),
            target_niche=request.form.get("target_niche", "").strip(),
            target_platforms=request.form.get("target_platforms", "").strip(),
            target_country=request.form.get("target_country", "").strip(),
            budget_min=request.form.get("budget_min", type=int) or 0,
            budget_max=request.form.get("budget_max", type=int) or 0,
            goal=request.form.get("goal", "").strip(),
            brief=request.form.get("brief", "").strip(),
            deliverables=request.form.get("deliverables", "").strip(),
        )

        required = [
            campaign.title,
            campaign.industry,
            campaign.target_niche,
            campaign.target_platforms,
            campaign.target_country,
            campaign.goal,
            campaign.brief,
            campaign.deliverables,
        ]
        if not all(required) or campaign.budget_max <= 0:
            flash("Complete the required campaign fields and budget.", "warning")
            return redirect(url_for("campaigns.new_campaign"))

        if campaign.budget_min > campaign.budget_max:
            flash("Minimum budget cannot be higher than maximum budget.", "warning")
            return redirect(url_for("campaigns.new_campaign"))

        db.session.add(campaign)
        db.session.commit()
        flash("Campaign brief posted. Collabry is ready to score creator matches.", "success")
        return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign.id))

    return render_template("campaign_new.html")


@campaigns_bp.route("/<int:campaign_id>")
def campaign_detail(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    scored_creators = []
    if current_user.is_authenticated and current_user.id == campaign.business_id:
        creators = CreatorProfile.query.order_by(CreatorProfile.followers.desc()).all()
        scored_creators = score_creators_for_campaign(campaign, creators)
    elif current_user.is_authenticated and current_user.role == "influencer" and current_user.creator_profile:
        scored_creators = [(current_user.creator_profile, calculate_match_score(campaign, current_user.creator_profile))]

    return render_template("campaign_detail.html", campaign=campaign, scored_creators=scored_creators)


@campaigns_bp.route("/<int:campaign_id>/apply", methods=["GET", "POST"])
@login_required
def apply(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if not is_influencer():
        flash("Only influencers can apply to campaigns.", "danger")
        return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign.id))

    profile = current_user.creator_profile
    if profile is None:
        flash("Create your creator profile before applying to campaigns.", "warning")
        return redirect(url_for("creators.onboarding"))

    score = calculate_match_score(campaign, profile)
    if request.method == "POST":
        collaboration_request = CollaborationRequest(
            campaign_id=campaign.id,
            creator_profile_id=profile.id,
            sender_id=current_user.id,
            direction="influencer_application",
            message=request.form.get("message", "").strip(),
            match_score=score,
        )
        db.session.add(collaboration_request)
        try:
            db.session.commit()
            flash("Application sent to the business.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("You already have a request for this campaign.", "info")
        return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign.id))

    return render_template("campaign_apply.html", campaign=campaign, profile=profile, score=score)
