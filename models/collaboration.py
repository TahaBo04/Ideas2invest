from datetime import datetime
from extensions import db


class CollaborationAgreement(db.Model):
    __tablename__ = "collaboration_agreements"

    id = db.Column(db.Integer, primary_key=True)
    creator_profile_id = db.Column(db.Integer, db.ForeignKey("creator_profiles.id"), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    accepted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(255))

    creator_profile = db.relationship("CreatorProfile", back_populates="agreements")
    business = db.relationship("User", backref="collaboration_agreements")

    __table_args__ = (
        db.UniqueConstraint("creator_profile_id", "business_id", name="uq_creator_business_agreement"),
    )


class CollaborationRequest(db.Model):
    __tablename__ = "collaboration_requests"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    creator_profile_id = db.Column(db.Integer, db.ForeignKey("creator_profiles.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    direction = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    message = db.Column(db.Text)
    match_score = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign = db.relationship("Campaign", back_populates="requests")
    creator_profile = db.relationship("CreatorProfile", back_populates="requests")
    sender = db.relationship("User", backref="sent_collaboration_requests")

    __table_args__ = (
        db.UniqueConstraint("campaign_id", "creator_profile_id", name="uq_campaign_creator_request"),
    )
