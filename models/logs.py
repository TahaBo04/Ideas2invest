# models/logs.py
from datetime import datetime
from extensions import db


class UserLoginLog(db.Model):
    __tablename__ = "user_login_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    success = db.Column(db.Boolean, nullable=False)

    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.Text)
    failure_reason = db.Column(db.String(120))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class IdeaViewLog(db.Model):
    __tablename__ = "idea_view_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)

    action = db.Column(db.String(40), default="view", nullable=False)
    # examples: view, open_confidential, request_nda, download

    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.Text)
    extra = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(db.Model):
    """
    Generic audit log for any sensitive action:
    - NDA accepted
    - Idea created/edited/deleted
    - Investor requested access
    - Admin verified KYC
    - Anything you want to prove later
    """
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    target_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"))

    event_type = db.Column(db.String(60), nullable=False)   # e.g. "kyc_submitted", "nda_signed"
    description = db.Column(db.Text)                        # human-readable explanation
    metadata_json = db.Column(db.Text)                      # store JSON as text for SQLite MVP

    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
