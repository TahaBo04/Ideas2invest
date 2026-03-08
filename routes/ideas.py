# routes/ideas.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from models.idea import Idea
from services.security_service import can_view_nda_layer
from services.nda_service import has_signed_nda, sign_nda
from services.logging_service import log_idea_view

ideas_bp = Blueprint("ideas", __name__, url_prefix="/ideas")


@ideas_bp.route("/")
def list_ideas():
    ideas = Idea.query.order_by(Idea.id.desc()).all()
    return render_template("ideas_list.html", ideas=ideas)


# 🔵 Layer 1 — Public teaser (SAFE)
@ideas_bp.route("/<int:idea_id>/public")
def idea_public(idea_id):
    idea = Idea.query.get_or_404(idea_id)

    viewer_id = current_user.id if current_user.is_authenticated else None
    log_idea_view(idea_id=idea.id, viewed_layer="public", viewer_id=viewer_id)

    return render_template("idea_public.html", idea=idea)


# 🔵 Layer 2 — NDA gate (Investors only + KYC)
@ideas_bp.route("/<int:idea_id>/nda", methods=["GET", "POST"])
@login_required
def idea_nda_confirm(idea_id):
    idea = Idea.query.get_or_404(idea_id)

    if not can_view_nda_layer():
        flash("Accès réservé aux investisseurs vérifiés (KYC).", "danger")
        return redirect(url_for("ideas.idea_public", idea_id=idea.id))

    if has_signed_nda(current_user.id, idea.id):
        return redirect(url_for("ideas.idea_confidential", idea_id=idea.id))

    if request.method == "POST":
        # accept NDA
        sign_nda(user_id=current_user.id, idea_id=idea.id)
        flash("NDA accepté. Accès accordé au contenu confidentiel.", "success")
        return redirect(url_for("ideas.idea_confidential", idea_id=idea.id))

    return render_template("idea_nda_confirm.html", idea=idea)


# 🔵 Layer 3 — Confidential core (only after NDA)
@ideas_bp.route("/<int:idea_id>/confidential")
@login_required
def idea_confidential(idea_id):
    idea = Idea.query.get_or_404(idea_id)

    if not can_view_nda_layer():
        flash("Accès réservé aux investisseurs vérifiés (KYC).", "danger")
        return redirect(url_for("ideas.idea_public", idea_id=idea.id))

    if not has_signed_nda(current_user.id, idea.id):
        flash("Veuillez accepter le NDA avant d’accéder au contenu confidentiel.", "warning")
        return redirect(url_for("ideas.idea_nda_confirm", idea_id=idea.id))

    # Log confidential view (strong proof)
    log_idea_view(idea_id=idea.id, viewed_layer="confidential", viewer_id=current_user.id)

    return render_template("idea_confidential.html", idea=idea)
