# models/idea.py
from datetime import datetime
from extensions import db


class Idea(db.Model):
    __tablename__ = "ideas"

    id = db.Column(db.Integer, primary_key=True)

    # Owner (innovator who posted the idea)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Public layer (safe to show)
    title = db.Column(db.String(140), nullable=False)
    sector = db.Column(db.String(80), nullable=True)
    country = db.Column(db.String(80), nullable=True)
    stage = db.Column(db.String(40), nullable=True)
    teaser = db.Column(db.Text, nullable=False)

    # NDA-protected layer (semi-confidential)
    nda_preview = db.Column(db.Text, nullable=True)

    # Fully confidential pitch (only after NDA)
    confidential_pitch = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    owner = db.relationship("User", back_populates="ideas")

    def __repr__(self) -> str:
        return f"<Idea id={self.id} title={self.title!r} owner_id={self.owner_id}>"
