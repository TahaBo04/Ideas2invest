# models/user.py
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
    role = db.Column(db.String(20), nullable=False)

    id_type = db.Column(db.String(30))
    id_number = db.Column(db.String(50))
    id_document_path = db.Column(db.String(255))
    kyc_verified = db.Column(db.Boolean, default=False)

    # KYC verification workflow
    verification_status = db.Column(db.String(20), default="pending")
    verification_notes = db.Column(db.Text)

    # Public profile fields
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ideas = db.relationship("Idea", back_populates="owner")
