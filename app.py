from flask import Flask, render_template
from config import Config
from extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from models.user import User
    from models import campaign, collaboration, creator, logs, user  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    from routes.auth import auth_bp
    from routes.creators import creators_bp
    from routes.campaigns import campaigns_bp
    from routes.business import business_bp
    from routes.influencer import influencer_bp
    from routes.admin import admin_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(creators_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(business_bp)
    app.register_blueprint(influencer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)

    @app.route("/")
    def home():
        from models.campaign import Campaign
        from models.creator import CreatorProfile

        from models.user import User

        creators = (
            CreatorProfile.query.join(CreatorProfile.user)
            .filter(User.verification_status == "verified")
            .order_by(CreatorProfile.followers.desc())
            .limit(3)
            .all()
        )
        campaigns = (
            Campaign.query.join(Campaign.business)
            .filter(Campaign.status == "open")
            .filter(User.verification_status == "verified")
            .order_by(Campaign.created_at.desc())
            .limit(3)
            .all()
        )
        return render_template("home.html", creators=creators, campaigns=campaigns)

    return app


if __name__ == "__main__":
    import os

    app = create_app()
    with app.app_context():
        db.create_all()
        from services.schema_service import ensure_runtime_schema

        ensure_runtime_schema()
        if os.environ.get("COLLABRY_DEMO") == "1":
            from services.demo_seed import seed_demo_data

            seed_demo_data()
    app.run(debug=True, use_reloader=False)
