# services/security_service.py
from flask_login import current_user

def is_verified_user() -> bool:
    """
    KYC gate. If you don't yet store kyc_status, this returns True to not block dev.
    Later: return current_user.kyc_status == "approved"
    """
    if not current_user.is_authenticated:
        return False

    # If your User model has kyc_status, enforce it.
    kyc_status = getattr(current_user, "kyc_status", None)
    if kyc_status is None:
        return True  # dev fallback

    return kyc_status == "approved"


def can_view_nda_layer() -> bool:
    """Only investors should view NDA/confidential layers."""
    return current_user.is_authenticated and current_user.role == "investor" and is_verified_user()
