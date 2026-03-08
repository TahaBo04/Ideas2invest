# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import models so they are registered
    from models.user import User
    from models import user, idea, nda, logs, post  # noqa: F401

    # --- Flask-Login user loader ---
    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprints
    from routes.auth import auth_bp
    from routes.ideas import ideas_bp
    from routes.investor import investor_bp
    from routes.admin import admin_bp
    from routes.posts import posts_bp


    app.register_blueprint(posts_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ideas_bp)
    app.register_blueprint(investor_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home():
        return render_template("base.html")

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
