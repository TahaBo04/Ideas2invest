from datetime import datetime
from app import db

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author_role = db.Column(db.String(20), nullable=False)  # 'investor' or 'innovator'

    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)

    visibility = db.Column(db.String(20), default="public")  
    # public | verified_only | investors_only | innovators_only

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    author = db.relationship("User", backref="posts")
