import sys
import os
import logging

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    try:
        db.create_all()
    except Exception:
        logging.exception("db.create_all() failed during startup")
