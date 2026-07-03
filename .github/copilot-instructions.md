# Copilot Instructions for Collabry

## Project Overview

Collabry is a Viral Talent Flask marketplace connecting influencers with businesses looking for creator-led ad campaigns. The app supports creator media kits, business campaign briefs, deterministic match scoring, collaboration requests, protected media-kit access, and admin verification.

## Tech Stack

- Python 3.12
- Flask 3.0.2
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- SQLite locally, PostgreSQL through `DATABASE_URL` in production
- Jinja2 templates with custom CSS
- Vercel Python serverless deployment through `api/index.py`

## Architecture Rules

- Use `create_app()` in `app.py`.
- Import `db` and `login_manager` from `extensions.py`, never from `app.py`.
- Keep database models in `models/`.
- Keep route handlers in Flask blueprints under `routes/`.
- Keep business logic in `services/`.
- Register every new blueprint in `create_app()`.
- Import every new model module in `create_app()` so SQLAlchemy registers the tables.

## Domain Rules

- Roles are `influencer`, `business`, and `admin`.
- Creator profile data belongs in `CreatorProfile`.
- Campaign brief data belongs in `Campaign`.
- Business invites and influencer applications belong in `CollaborationRequest`.
- Protected creator access requires `CollaborationAgreement`.
- Smart matching should remain deterministic unless the product explicitly adds a live AI provider.

## Local Run

```bash
pip install -r requirements.txt
COLLABRY_DEMO=1 python app.py
```

The app runs at `http://127.0.0.1:5000`.

## Safety

- Never commit `.env`, `.db`, `.sqlite3`, virtual environments, or generated upload files.
- `COLLABRY_DEMO=1` is the only supported automatic demo seed path.
- Do not add payments, live chat, or external AI calls unless explicitly requested.
