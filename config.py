# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# On Vercel the project directory is read-only; only /tmp is writable.
_db_dir = "/tmp" if os.environ.get("VERCEL") else BASE_DIR


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(_db_dir, 'ideas2invest.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB upload limit
