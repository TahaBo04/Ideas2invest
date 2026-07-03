from flask_login import current_user


def is_verified_user() -> bool:
    if not current_user.is_authenticated:
        return False
    return getattr(current_user, "verification_status", None) == "verified"


def is_business() -> bool:
    return current_user.is_authenticated and current_user.role == "business"


def is_influencer() -> bool:
    return current_user.is_authenticated and current_user.role == "influencer"


def can_view_protected_creator_details() -> bool:
    return is_business() and is_verified_user()
