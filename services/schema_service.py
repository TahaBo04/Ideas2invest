from __future__ import annotations

from sqlalchemy import inspect, text

from extensions import db


def ensure_runtime_schema() -> None:
    if db.engine.dialect.name != "sqlite":
        return

    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "company_name": "VARCHAR(120)",
        "company_website": "VARCHAR(255)",
        "social_profile_url": "VARCHAR(255)",
        "verification_submitted_at": "DATETIME",
    }

    for column, ddl in additions.items():
        if column not in existing:
            db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column} {ddl}"))

    db.session.commit()
