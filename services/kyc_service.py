# services/kyc_service.py
from __future__ import annotations

"""
Identity verification helpers for Collabry.
"""

from extensions import db
from models.user import User


def submit_kyc(user: User, id_type: str, id_number: str, id_document_path: str | None = None):
    """
    Called when the user fills identity info or uploads ID doc.
    """
    user.id_type = id_type
    user.id_number = id_number
    if id_document_path:
        user.id_document_path = id_document_path
    user.verification_status = "pending"
    db.session.commit()
    return user


def validate_id_format(id_type: str, id_number: str) -> tuple[bool, str | None]:
    id_number = (id_number or "").strip().upper()

    if not id_number:
        return False, "The identity document number is required."

    if id_type.upper() in ("CIN", "CNI"):
        if len(id_number) < 5 or len(id_number) > 10:
            return False, "The CIN/CNI number length looks invalid."
        if not any(c.isalpha() for c in id_number) or not any(c.isdigit() for c in id_number):
            return False, "The CIN/CNI number should include letters and digits."

    if id_type.lower() == "passport":
        if len(id_number) < 6:
            return False, "The passport number is too short."
        if not id_number.isalnum():
            return False, "The passport number should be alphanumeric."

    if len(id_number) < 4:
        return False, "The identity document number is too short."

    return True, None


def mark_user_verified(user: User, notes: str | None = None):
    user.verification_status = "verified"
    if notes:
        user.verification_notes = (user.verification_notes or "") + f"\n[VERIFIED] {notes}"
    db.session.commit()
    return user
