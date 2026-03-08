# services/kyc_service.py
"""
KYC (Know Your Customer) utilities for ideas2invest.

Here we manage:
- Submitting identity info
- Marking users as verified / rejected
- Simple local validation of ID formats
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
    """
    Very simple local checks to avoid obvious fake IDs.
    You can later extend this or integrate with a real KYC API.
    """
    id_number = (id_number or "").strip().upper()

    if not id_number:
        return False, "Le numéro de pièce d'identité ne peut pas être vide."

    # Simple example for Moroccan CIN (often 1–2 letters + up to 6 digits)
    if id_type.upper() in ("CIN", "CNI"):
        if len(id_number) < 5 or len(id_number) > 10:
            return False, "Format CIN suspect (longueur invalide)."
        if not any(c.isalpha() for c in id_number) or not any(c.isdigit() for c in id_number):
            return False, "Le CIN doit contenir au moins une lettre et des chiffres."

    # Simple passport check: length + alphanumeric
    if id_type.lower() == "passport":
        if len(id_number) < 6:
            return False, "Numéro de passeport trop court."
        if not id_number.isalnum():
            return False, "Numéro de passeport invalide (caractères non autorisés)."

    # Default: minimal check
    if len(id_number) < 4:
        return False, "Numéro de pièce trop court."

    return True, None


def mark_user_verified(user: User, notes: str | None = None):
    user.verification_status = "verified"
    if notes:
        user.verification_notes = (user.verification_notes or "") + f"\n[VERIFIED] {notes}"
    db.session.commit()
    return user
