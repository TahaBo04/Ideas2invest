# services/nda_service.py
from flask import request
from app import db
from models.nda import NDAAgreement

def has_signed_nda(user_id: int, idea_id: int) -> bool:
    return (
        NDAAgreement.query
        .filter_by(user_id=user_id, idea_id=idea_id)
        .first()
        is not None
    )

def sign_nda(user_id: int, idea_id: int):
    nda = NDAAgreement(
        user_id=user_id,
        idea_id=idea_id,
        ip_address=(request.headers.get("X-Forwarded-For") or request.remote_addr),
        user_agent=request.headers.get("User-Agent", "")[:255],
    )
    db.session.add(nda)
    db.session.commit()
