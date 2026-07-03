from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="influencer")

    id_type = db.Column(db.String(30))
    id_number = db.Column(db.String(50))
    id_document_path = db.Column(db.String(255))
    company_name = db.Column(db.String(120))
    company_website = db.Column(db.String(255))
    social_profile_url = db.Column(db.String(255))
    verification_status = db.Column(db.String(20), default="pending")
    verification_notes = db.Column(db.Text)
    verification_submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    creator_profile = db.relationship(
        "CreatorProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    campaigns = db.relationship("Campaign", back_populates="business", cascade="all, delete-orphan")

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_verified(self) -> bool:
        return self.verification_status == "verified"
