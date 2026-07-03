from __future__ import annotations

from flask import request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.collaboration import CollaborationAgreement


def has_collaboration_agreement(business_id: int, creator_profile_id: int) -> bool:
    return (
        CollaborationAgreement.query.filter_by(
            business_id=business_id,
            creator_profile_id=creator_profile_id,
        ).first()
        is not None
    )


def accept_collaboration_agreement(business_id: int, creator_profile_id: int) -> CollaborationAgreement:
    existing = CollaborationAgreement.query.filter_by(
        business_id=business_id,
        creator_profile_id=creator_profile_id,
    ).first()
    if existing:
        return existing

    agreement = CollaborationAgreement(
        business_id=business_id,
        creator_profile_id=creator_profile_id,
        ip_address=(request.headers.get("X-Forwarded-For") or request.remote_addr),
        user_agent=request.headers.get("User-Agent", "")[:255],
    )
    db.session.add(agreement)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        agreement = CollaborationAgreement.query.filter_by(
            business_id=business_id,
            creator_profile_id=creator_profile_id,
        ).first()
    return agreement
