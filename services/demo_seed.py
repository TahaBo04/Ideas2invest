from __future__ import annotations

from werkzeug.security import generate_password_hash

from extensions import db
from models.campaign import Campaign
from models.collaboration import CollaborationRequest
from models.creator import CreatorProfile
from models.user import User
from services.matching_service import calculate_match_score


def _user(email: str, first_name: str, last_name: str, role: str) -> User:
    existing = User.query.filter_by(email=email).first()
    if existing:
        return existing

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        password_hash=generate_password_hash("collabry123"),
        id_type="passport",
        id_number=f"DEMO-{role}-{first_name}".upper(),
        verification_status="verified",
        verification_submitted_at=None,
        bio="Demo account for the local Collabry marketplace.",
    )
    db.session.add(user)
    db.session.flush()
    return user


def seed_demo_data() -> None:
    if User.query.filter_by(email="brand@collabry.local").first():
        return

    admin = _user("admin@collabry.local", "Viral", "Talent", "admin")
    brand = _user("brand@collabry.local", "Maya", "Brands", "business")
    creator_a = _user("lina@collabry.local", "Lina", "Reels", "influencer")
    creator_b = _user("samir@collabry.local", "Samir", "Fit", "influencer")
    creator_c = _user("nora@collabry.local", "Nora", "Style", "influencer")

    brand.company_name = "Viral Talent Demo Brand"
    brand.company_website = "https://viraltalent.co/"
    brand.id_type = "business_registration"
    creator_a.social_profile_url = "https://instagram.com/lina.reels"
    creator_b.social_profile_url = "https://instagram.com/samir.fit"
    creator_c.social_profile_url = "https://tiktok.com/@norastylelab"

    profiles = [
        CreatorProfile(
            user_id=creator_a.id,
            display_name="Lina Reels",
            niche="Beauty",
            platforms="TikTok, Instagram",
            audience_country="Morocco",
            followers=184000,
            engagement_rate=6.8,
            starting_rate=900,
            media_kit_summary="Short-form beauty creator known for fast product education, before/after routines, and high-save tutorials.",
            protected_details="Average CPV: $0.018. Best-performing format: 18-25 second routine demo. WhatsApp: +212 600 000 001.",
        ),
        CreatorProfile(
            user_id=creator_b.id,
            display_name="Samir Fit",
            niche="Fitness",
            platforms="Instagram, YouTube Shorts",
            audience_country="France",
            followers=92000,
            engagement_rate=4.4,
            starting_rate=700,
            media_kit_summary="Fitness creator with a strong male 18-34 audience and practical supplement, apparel, and app-install content.",
            protected_details="Average story swipe rate: 3.2%. Bundle: 1 Reel + 3 stories. Email: samir.fit@example.com.",
        ),
        CreatorProfile(
            user_id=creator_c.id,
            display_name="Nora Style Lab",
            niche="Fashion",
            platforms="TikTok, Pinterest, Instagram",
            audience_country="United States",
            followers=267000,
            engagement_rate=5.7,
            starting_rate=1400,
            media_kit_summary="Fashion and styling creator producing lookbooks, try-on hauls, and creator-led paid social assets.",
            protected_details="Top segment: women 21-34. Paid usage uplift available for 30/60/90 days. Email: partnerships@nora.example.",
        ),
    ]
    db.session.add_all(profiles)
    db.session.flush()

    campaigns = [
        Campaign(
            business_id=brand.id,
            title="Launch a Gen Z skincare routine in Morocco",
            industry="Beauty",
            target_niche="Beauty",
            target_platforms="TikTok, Instagram",
            target_country="Morocco",
            budget_min=600,
            budget_max=1600,
            goal="Drive creator-led awareness and trackable landing-page visits.",
            brief="We need authentic short-form videos showing the morning routine, texture, and why the formula fits humid weather.",
            deliverables="2 TikToks, 1 Instagram Reel, 3 story frames, 30-day paid usage rights.",
        ),
        Campaign(
            business_id=brand.id,
            title="Performance creatives for a fitness app trial",
            industry="Mobile Apps",
            target_niche="Fitness",
            target_platforms="Instagram, YouTube Shorts",
            target_country="France",
            budget_min=500,
            budget_max=1200,
            goal="Acquire free-trial users from creator testimonial content.",
            brief="Show a realistic seven-day challenge, app screenshots, and a simple invitation to start the trial.",
            deliverables="1 Reel, 1 YouTube Short, raw files for paid ads.",
        ),
    ]
    db.session.add_all(campaigns)
    db.session.flush()

    demo_request = CollaborationRequest(
        campaign_id=campaigns[0].id,
        creator_profile_id=profiles[0].id,
        sender_id=brand.id,
        direction="business_invite",
        message="Your tutorial format is a strong fit for this skincare launch.",
        match_score=calculate_match_score(campaigns[0], profiles[0]),
    )
    db.session.add(demo_request)

    admin.verification_notes = "Demo admin account."
    db.session.commit()
