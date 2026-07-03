from __future__ import annotations

import os
import uuid

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_VERIFICATION_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}


def allowed_verification_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_VERIFICATION_EXTENSIONS


def get_verification_upload_dir() -> str:
    if os.environ.get("VERCEL"):
        upload_dir = "/tmp/collabry_verification_docs"
    else:
        upload_dir = os.path.join(current_app.instance_path, "verification_docs")
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def save_verification_document(file: FileStorage, role: str) -> str:
    original = secure_filename(file.filename or "")
    ext = original.rsplit(".", 1)[1].lower()
    filename = f"{role}-{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(get_verification_upload_dir(), filename))
    return filename
