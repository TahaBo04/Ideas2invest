from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.campaign import Campaign
from models.collaboration import CollaborationRequest
from models.creator import CreatorProfile
from services.collaboration_service import accept_collaboration_agreement, has_collaboration_agreement
from services.logging_service import log_audit_event, log_creator_view
from services.matching_service import calculate_match_score
from services.security_service import can_view_protected_creator_details, is_business, is_influencer

creators_bp = Blueprint("creators", __name__, url_prefix="/creators")


@creators_bp.route("/")
def list_creators():
    niche = request.args.get("niche", "").strip()
    platform = request.args.get("platform", "").strip()
    country = request.args.get("country", "").strip()

    query = CreatorProfile.query
    if niche:
        query = query.filter(CreatorProfile.niche.ilike(f"%{niche}%"))
    if platform:
        query = query.filter(CreatorProfile.platforms.ilike(f"%{platform}%"))
    if country:
        query = query.filter(CreatorProfile.audience_country.ilike(f"%{country}%"))

    creators = query.order_by(CreatorProfile.followers.desc()).all()
    campaign = None
    scores = {}
    campaign_id = request.args.get("campaign_id", type=int)
    if campaign_id:
        campaign = Campaign.query.get(campaign_id)
    elif current_user.is_authenticated and current_user.role == "business":
        campaign = Campaign.query.filter_by(business_id=current_user.id, status="open").order_by(Campaign.id.desc()).first()

    if campaign:
        scores = {creator.id: calculate_match_score(campaign, creator) for creator in creators}

    return render_template("creators_list.html", creators=creators, scores=scores, campaign=campaign)


@creators_bp.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    if not is_influencer():
        flash("Only influencer accounts can create a creator profile.", "danger")
        return redirect(url_for("home"))

    profile = current_user.creator_profile
    if request.method == "POST":
        if profile is None:
            profile = CreatorProfile(user_id=current_user.id, display_name=current_user.display_name)
            db.session.add(profile)

        profile.display_name = request.form.get("display_name", current_user.display_name).strip()
        profile.niche = request.form.get("niche", "").strip()
        profile.platforms = request.form.get("platforms", "").strip()
        profile.audience_country = request.form.get("audience_country", "").strip()
        profile.followers = request.form.get("followers", type=int) or 0
        profile.engagement_rate = request.form.get("engagement_rate", type=float) or 0.0
        profile.starting_rate = request.form.get("starting_rate", type=int) or 0
        profile.media_kit_summary = request.form.get("media_kit_summary", "").strip()
        profile.protected_details = request.form.get("protected_details", "").strip()

        required = [profile.display_name, profile.niche, profile.platforms, profile.audience_country, profile.media_kit_summary]
        if not all(required):
            flash("Complete the required profile fields so businesses can evaluate you.", "warning")
            return redirect(url_for("creators.onboarding"))

        db.session.commit()
        flash("Creator profile saved.", "success")
        return redirect(url_for("creators.creator_detail", creator_id=profile.id))

    return render_template("creator_onboarding.html", profile=profile)


@creators_bp.route("/<int:creator_id>")
def creator_detail(creator_id):
    creator = CreatorProfile.query.get_or_404(creator_id)
    viewer_id = current_user.id if current_user.is_authenticated else None
    log_creator_view(creator_profile_id=creator.id, action="public", viewer_id=viewer_id)

    campaigns = []
    scores = {}
    can_view_protected = False
    if current_user.is_authenticated and current_user.role == "business":
        campaigns = Campaign.query.filter_by(business_id=current_user.id, status="open").order_by(Campaign.id.desc()).all()
        scores = {campaign.id: calculate_match_score(campaign, creator) for campaign in campaigns}
        can_view_protected = has_collaboration_agreement(current_user.id, creator.id)

    return render_template(
        "creator_detail.html",
        creator=creator,
        campaigns=campaigns,
        scores=scores,
        can_view_protected=can_view_protected,
    )


@creators_bp.route("/<int:creator_id>/agreement", methods=["GET", "POST"])
@login_required
def agreement(creator_id):
    creator = CreatorProfile.query.get_or_404(creator_id)
    if not can_view_protected_creator_details():
        flash("Protected creator details are reserved for verified business accounts.", "danger")
        return redirect(url_for("creators.creator_detail", creator_id=creator.id))

    if request.method == "POST":
        accept_collaboration_agreement(current_user.id, creator.id)
        log_audit_event(
            event_type="collaboration_agreement_accepted",
            description=f"{current_user.display_name} accepted access terms for {creator.display_name}.",
            actor_user_id=current_user.id,
            target_user_id=creator.user_id,
            creator_profile_id=creator.id,
        )
        flash("Agreement accepted. Protected media-kit details unlocked.", "success")
        return redirect(url_for("creators.media_kit", creator_id=creator.id))

    return render_template("creator_agreement.html", creator=creator)


@creators_bp.route("/<int:creator_id>/media-kit")
@login_required
def media_kit(creator_id):
    creator = CreatorProfile.query.get_or_404(creator_id)
    if not can_view_protected_creator_details():
        flash("Protected media-kit access is reserved for verified business accounts.", "danger")
        return redirect(url_for("creators.creator_detail", creator_id=creator.id))
    if not has_collaboration_agreement(current_user.id, creator.id):
        flash("Accept the collaboration agreement before opening protected details.", "warning")
        return redirect(url_for("creators.agreement", creator_id=creator.id))

    log_creator_view(creator_profile_id=creator.id, action="protected", viewer_id=current_user.id)
    return render_template("creator_media_kit.html", creator=creator)


@creators_bp.route("/<int:creator_id>/invite", methods=["POST"])
@login_required
def invite_creator(creator_id):
    creator = CreatorProfile.query.get_or_404(creator_id)
    if not is_business():
        flash("Only business accounts can invite creators.", "danger")
        return redirect(url_for("creators.creator_detail", creator_id=creator.id))

    campaign_id = request.form.get("campaign_id", type=int)
    campaign = Campaign.query.filter_by(id=campaign_id, business_id=current_user.id).first_or_404()
    message = request.form.get("message", "").strip()
    score = calculate_match_score(campaign, creator)

    collaboration_request = CollaborationRequest(
        campaign_id=campaign.id,
        creator_profile_id=creator.id,
        sender_id=current_user.id,
        direction="business_invite",
        message=message,
        match_score=score,
    )
    db.session.add(collaboration_request)
    try:
        db.session.commit()
        flash("Creator invited to your campaign.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("This creator already has a request for that campaign.", "info")

    return redirect(url_for("creators.creator_detail", creator_id=creator.id))
