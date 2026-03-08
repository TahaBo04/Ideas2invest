# models/nda.py
from datetime import datetime
from app import db

class NDAAgreement(db.Model):
    __tablename__ = "nda_agreements"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    accepted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    idea = db.relationship("Idea", backref="nda_agreements")
    user = db.relationship("User", backref="nda_agreements")

    __table_args__ = (
        db.UniqueConstraint("idea_id", "user_id", name="uq_nda_idea_user"),
    )
