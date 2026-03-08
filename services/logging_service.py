# services/logging_service.py
from datetime import datetime
from flask import request
from app import db

from models.logs import UserLoginLog, IdeaViewLog


def log_login(user, success: bool, failure_reason: str | None = None):
    log = UserLoginLog(
        user_id=user.id,  # ✅ use user.id
        success=success,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        failure_reason=failure_reason,
        created_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()


def log_idea_view(user, idea, action: str = "view", extra: str | None = None):
    """
    Logs an investor/innovator view/action on an idea.
    action examples: "view", "open_confidential", "download", "request_nda"
    """
    log = IdeaViewLog(
        user_id=user.id,          # ✅ use IDs
        idea_id=idea.id,
        action=action,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        extra=extra,
        created_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()
