# services/logging_service.py
from __future__ import annotations

from datetime import datetime
from flask import request
from extensions import db

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


def log_idea_view(idea_id: int, viewed_layer: str, viewer_id: int | None = None):
    """
    Logs an investor/innovator view/action on an idea.
    viewed_layer examples: "public", "confidential"
    """
    if viewer_id is None:
        return
    log = IdeaViewLog(
        user_id=viewer_id,
        idea_id=idea_id,
        action=viewed_layer,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        created_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()
