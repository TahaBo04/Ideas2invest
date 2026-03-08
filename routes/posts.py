from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.post import Post

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.route("/")
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
    return render_template("posts_feed.html", posts=posts)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
    # Only investors and innovators can post
    if current_user.role not in ("investor", "innovator"):
        flash("Vous n’avez pas l’autorisation de publier.", "danger")
        return redirect(url_for("posts.feed"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        visibility = request.form.get("visibility", "public")

        if not title or not content:
            flash("Titre et contenu obligatoires.", "warning")
            return redirect(url_for("posts.new_post"))

        post = Post(
            author_id=current_user.id,
            author_role=current_user.role,
            title=title,
            content=content,
            visibility=visibility,
        )
        db.session.add(post)
        db.session.commit()

        flash("Post publié ✅", "success")
        return redirect(url_for("posts.feed"))

    return render_template("post_new.html")
