# Copilot Instructions for Ideas2invest

## Project Overview

Ideas2invest is a B2B web platform where innovators can share business ideas with investors under structured confidentiality controls. It features a three-layer idea confidentiality system (public teaser → NDA-protected preview → full confidential pitch), KYC verification, role-based access control, and an audit trail.

## Tech Stack

- **Language:** Python 3.12 (pinned in `.python-version`)
- **Framework:** Flask 3.0.2
- **ORM:** Flask-SQLAlchemy 3.1.1 with SQLite (local) or PostgreSQL (production via `DATABASE_URL`)
- **Authentication:** Flask-Login 0.6.3, Werkzeug for password hashing
- **Templating:** Jinja2 3.1.3
- **Deployment:** Vercel (serverless Python via `api/index.py`)
- **Production server:** Gunicorn 22.0.0

## Architecture

```
app.py              → Flask application factory (create_app)
config.py           → Configuration (Config class, Vercel detection)
extensions.py       → Shared Flask extensions (db, login_manager)
api/index.py        → Vercel serverless entry point
models/             → SQLAlchemy models (User, Idea, NDAAgreement, Post, logs)
routes/             → Flask Blueprints (auth, ideas, investor, admin, posts, profile)
services/           → Business logic (nda_service, security_service, kyc_service, logging_service)
templates/          → Jinja2 HTML templates
static/css/         → Custom CSS
static/uploads/     → User-uploaded files
```

### Key Patterns

- **Application factory:** Use `create_app()` in `app.py` to create the Flask app.
- **Extensions in `extensions.py`:** `db` (SQLAlchemy) and `login_manager` (Flask-Login) are initialized in `extensions.py` and imported by models and routes. Never import them from `app.py`.
- **Blueprints:** Each route module defines a Blueprint registered in `create_app()`.
- **Services layer:** Business logic lives in `services/`, not in route handlers.
- **Vercel compatibility:** The filesystem is read-only on Vercel except `/tmp`. `config.py` detects the `VERCEL` env var and uses `/tmp` for the SQLite database path. File uploads also target `/tmp` on Vercel.

## Coding Conventions

- Use `from __future__ import annotations` in files that use `str | None` or other union type syntax for Python 3.9 compatibility.
- Models import `db` from `extensions`, not from `app`.
- Route files use Flask `Blueprint` and are registered in `app.py`.
- Use Werkzeug's `generate_password_hash` / `check_password_hash` for passwords.
- Keep business logic in `services/` and route handlers thin.

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
# The app runs at http://127.0.0.1:5000 with debug mode enabled
```

## Project Structure Rules

- Never commit `.env`, `.db` files, or anything in `static/uploads/profile_pics/` (except `.gitkeep`).
- Do not modify `api/index.py` unless changing the Vercel deployment setup.
- Do not modify `vercel.json` unless changing the Vercel routing or build configuration.
- All new database models go in `models/` and must be imported in `app.py` so they are registered with SQLAlchemy.
- All new route modules go in `routes/` as Blueprints and must be registered in `create_app()`.

## Database Models

- **User** — Roles: `innovator`, `investor`, `admin`. Includes KYC fields and verification status.
- **Idea** — Three-layer confidentiality: `teaser` (public), `nda_preview` (NDA-protected), `confidential_pitch` (full access after NDA).
- **NDAAgreement** — Records NDA signatures with IP address and user agent. Unique constraint on `(idea_id, user_id)`.
- **Post** — Social feed with visibility controls: `public`, `verified_only`, `investors_only`, `innovators_only`.
- **UserLoginLog, IdeaViewLog, AuditLog** — Audit and logging models in `models/logs.py`.

## Security Considerations

- Always validate KYC status before granting access to NDA or confidential layers.
- Log all sensitive actions (logins, idea views, NDA signatures) via `services/logging_service.py`.
- Never expose confidential pitch data without verifying NDA agreement via `services/nda_service.py`.
- Use role-based checks via `services/security_service.py` for protected routes.
