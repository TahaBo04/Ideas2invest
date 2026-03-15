# Ideas2invest — Full Technical Report

> **Platform:** B2B web application connecting innovators with investors under structured confidentiality controls.  
> **Last updated:** 2026-03-15

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Directory Structure](#3-directory-structure)
4. [Root-Level Files](#4-root-level-files)
5. [API Entry Point (`api/`)](#5-api-entry-point-api)
6. [Models (`models/`)](#6-models-models)
7. [Routes / Blueprints (`routes/`)](#7-routes--blueprints-routes)
8. [Services (`services/`)](#8-services-services)
9. [Templates (`templates/`)](#9-templates-templates)
10. [Static Assets (`static/`)](#10-static-assets-static)
11. [Data Flow & Key Workflows](#11-data-flow--key-workflows)
12. [Security Architecture](#12-security-architecture)
13. [Deployment Architecture](#13-deployment-architecture)

---

## 1. Project Overview

**Ideas2invest** is a Flask-based B2B web platform where innovators can share business ideas with vetted investors under a three-layer confidentiality model:

| Layer | Visibility | Access Condition |
|-------|-----------|-----------------|
| 1 – Public teaser | Everyone | None |
| 2 – NDA preview | KYC-verified investors | Accept digital NDA |
| 3 – Confidential pitch | KYC-verified investors | NDA already accepted |

Additional platform capabilities include:
- **KYC (Know Your Customer)** identity verification workflow for both innovators and investors.
- **Role-based access control** with three roles: `innovator`, `investor`, `admin`.
- **Community feed** with post visibility controls.
- **User profiles** with picture upload.
- **Full audit trail** capturing logins, idea views, NDA signings, and admin decisions.

---

## 2. Tech Stack

| Concern | Technology | Version |
|---------|-----------|---------|
| Language | Python | 3.12 |
| Web framework | Flask | 3.0.2 |
| ORM | Flask-SQLAlchemy | 3.1.1 |
| Database (local) | SQLite | — |
| Database (production) | PostgreSQL (via `DATABASE_URL`) | — |
| Authentication | Flask-Login | 0.6.3 |
| Password hashing | Werkzeug | 3.0.1 |
| Templating | Jinja2 | 3.1.3 |
| Production server | Gunicorn | 22.0.0 |
| Deployment | Vercel (serverless Python) | — |
| Frontend | Bootstrap 5 (CDN) + custom CSS | — |

---

## 3. Directory Structure

```
Ideas2invest/
├── api/
│   └── index.py               # Vercel serverless entry point
├── models/
│   ├── __init__.py            # Package init / model exports
│   ├── user.py                # User account model
│   ├── idea.py                # Three-layer idea model
│   ├── nda.py                 # NDA agreement records
│   ├── post.py                # Community feed posts
│   └── logs.py                # Audit/logging models
├── routes/
│   ├── __init__.py            # Package marker
│   ├── auth.py                # Register / Login / Logout
│   ├── ideas.py               # Three-layer idea routes
│   ├── investor.py            # Investor dashboard
│   ├── admin.py               # Admin KYC management
│   ├── posts.py               # Community feed
│   └── profile.py             # User profiles
├── services/
│   ├── __init__.py            # Package marker
│   ├── nda_service.py         # NDA signing & verification
│   ├── security_service.py    # Access control checks
│   ├── kyc_service.py         # KYC workflow helpers
│   └── logging_service.py     # Audit trail logging
├── static/
│   ├── css/style.css          # Custom design system
│   └── uploads/               # User-uploaded files
│       ├── logo.jpeg
│       └── profile_pics/      # Profile pictures (.gitkeep)
├── templates/                 # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── ideas_list.html
│   ├── idea_public.html
│   ├── idea_nda_confirm.html
│   ├── idea_confidential.html
│   ├── investor_dashboard.html
│   ├── posts_feed.html
│   ├── post_new.html
│   ├── admin_kyc_list.html
│   ├── profile_public.html
│   └── profile_edit.html
├── .github/
│   └── copilot-instructions.md # AI assistant dev guidelines
├── .gitignore
├── .python-version
├── app.py                     # Application factory
├── config.py                  # Configuration class
├── extensions.py              # Shared Flask extensions
├── requirements.txt
├── vercel.json                # Vercel deployment config
└── README.md
```

---

## 4. Root-Level Files

### `app.py` — Application Factory

**Purpose:** Creates and configures the Flask application. Acts as the central hub.

**Key responsibilities:**
- Defines `create_app(config_class=Config)` following the Flask application factory pattern.
- Initializes extensions: `db.init_app(app)` and `login_manager.init_app(app)`.
- Imports all model modules so SQLAlchemy can register their table definitions.
- Registers all six Blueprints: `auth_bp`, `ideas_bp`, `investor_bp`, `admin_bp`, `posts_bp`, `profile_bp`.
- Defines the home route `GET /` which renders `base.html`.
- Calls `db.create_all()` inside an app context to create missing tables on startup.
- Registers the `@login_manager.user_loader` callback that loads a `User` by primary key.

**Relationships:** Imports from `config.py`, `extensions.py`, all `models/`, and all `routes/`.

---

### `config.py` — Application Configuration

**Purpose:** Centralises all Flask and extension configuration in one `Config` class.

**Key settings:**

| Setting | Value |
|---------|-------|
| `SECRET_KEY` | `"dev-secret-change-me"` in development; read from `SECRET_KEY` env var in production |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:////tmp/ideas2invest.db` on Vercel; `sqlite:///ideas2invest.db` locally; overridden by `DATABASE_URL` env var for PostgreSQL |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` (disables unnecessary overhead) |
| `MAX_CONTENT_LENGTH` | `2 * 1024 * 1024` (2 MB file-upload limit) |

**Vercel detection:** Reads `os.environ.get("VERCEL")` and uses `/tmp` as the SQLite path because Vercel's filesystem is read-only everywhere except `/tmp`.

**Relationships:** Imported by `app.py` and `api/index.py`.

---

### `extensions.py` — Shared Flask Extensions

**Purpose:** Instantiates shared extension objects outside of the application factory to avoid circular imports.

**Objects defined:**

| Object | Type | Purpose |
|--------|------|---------|
| `db` | `SQLAlchemy()` | ORM instance imported by every model |
| `login_manager` | `LoginManager()` | Manages user sessions and `@login_required` |

`login_manager.login_view` is set to `"auth.login"` so unauthenticated requests are redirected to the login page.

**Relationships:** Imported by `app.py` (for `init_app` calls) and by every model file.

---

### `requirements.txt` — Python Dependencies

**Purpose:** Declares all runtime Python package dependencies.

| Package | Version | Role |
|---------|---------|------|
| Flask | 3.0.2 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM integration |
| Flask-Login | 0.6.3 | Session-based authentication |
| Werkzeug | 3.0.1 | Password hashing, WSGI utilities |
| Jinja2 | 3.1.3 | HTML templating |
| Gunicorn | 22.0.0 | Production WSGI server |

---

### `vercel.json` — Vercel Deployment Configuration

**Purpose:** Instructs Vercel how to build and route the application.

**Build rules:**
- `api/index.py` → Python serverless function (AWS Lambda-based).
- `static/**` → Served as static assets.

**Routing rules:**
1. `/static/*` → Static asset directory.
2. Everything else → `api/index.py` (Flask WSGI handler).

**Relationships:** Consumed by Vercel CI/CD; references `api/index.py`.

---

### `.gitignore` — Git Exclusion Rules

**Purpose:** Prevents sensitive and generated files from being committed.

Notable exclusions:
- `__pycache__/`, `*.pyc`, `*.pyo` — Python bytecode.
- `*.db`, `*.sqlite3` — Database files.
- `.env`, `.env.local` — Environment secrets.
- `.venv/`, `venv/` — Virtual environments.
- `static/uploads/profile_pics/*` (except `.gitkeep`) — User-uploaded images.
- `.idea/`, `.vscode/` — IDE project files.
- `build/`, `dist/`, `*.egg-info/` — Distribution artifacts.

---

### `.python-version` — Python Version Pin

**Purpose:** Tells `pyenv` (and compatible tools like `asdf`) which Python version to use.  
**Content:** `3.12`

---

### `README.md` — Project Documentation

**Purpose:** High-level documentation for developers and stakeholders.

**Sections:**
- Platform overview and value proposition.
- Key features: 3-layer confidentiality, KYC, NDA signing, audit trail.
- Role capabilities table (innovator / investor / admin).
- Workflow narrative: registration → KYC → idea posting → NDA → access.
- Tech stack summary.
- Annotated project structure.
- Getting started / local development instructions.
- Vercel deployment guide.
- Security considerations.

---

### `.github/copilot-instructions.md` — AI Development Guidelines

**Purpose:** Provides GitHub Copilot and AI coding assistants with project-specific context and conventions.

**Covers:**
- Architecture patterns (factory pattern, blueprints, services layer).
- Coding conventions (`from __future__ import annotations`, Werkzeug hashing, extension imports).
- Project rules (never commit secrets, model registration in `app.py`, blueprint registration in `create_app()`).
- Database model descriptions.
- Security checklist (KYC validation, audit logging, NDA verification).
- How to run the app locally.

---

## 5. API Entry Point (`api/`)

### `api/index.py` — Vercel Serverless Handler

**Purpose:** Wraps the Flask application for Vercel's Python serverless runtime.

**What it does:**
1. Adds the project root directory to `sys.path` so that `app`, `models`, `routes`, and `services` are importable.
2. Calls `create_app()` to get a configured Flask instance.
3. Initialises the database inside an app context — `db.create_all()` is called inside a `try/except` block so a startup failure doesn't crash the whole function; tables are created on cold starts when they don't yet exist.
4. Exports the `app` object — Vercel's runtime treats this as the WSGI handler.

**Relationships:** Depends on `app.py` and `config.py`. Referenced by `vercel.json`.

---

## 6. Models (`models/`)

All models use the shared `db` instance from `extensions.py`. They are imported in `app.py` to register their table definitions with SQLAlchemy.

### `models/__init__.py` — Package Initialiser

**Purpose:** Re-exports all model classes from the `models` package so other modules can import from a single location.

```python
from models.user import User
from models.idea import Idea
from models.nda import NDAAgreement
from models.post import Post
from models.logs import UserLoginLog, IdeaViewLog, AuditLog
```

---

### `models/user.py` — User Model

**Purpose:** Represents every registered account on the platform.

**Class:** `User(db.Model, UserMixin)`

**Table columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | Auto-increment primary key |
| `first_name` | String(50) | Given name |
| `last_name` | String(50) | Family name |
| `email` | String(120), unique | Login identifier |
| `password_hash` | String(256) | Werkzeug bcrypt hash |
| `role` | String(20) | `"innovator"`, `"investor"`, or `"admin"` |
| `id_type` | String(50) | KYC: document type (CIN, Passport, Other) |
| `id_number` | String(100) | KYC: document number |
| `id_document_path` | String(300) | KYC: path to uploaded scan |
| `kyc_verified` | Boolean | Convenience flag (True = verified) |
| `verification_status` | String(20) | `"pending"`, `"verified"`, or `"rejected"` |
| `verification_notes` | Text | Admin notes on KYC decision |
| `profile_picture` | String(300) | Relative path to uploaded profile image |
| `bio` | Text | Free-text biography |
| `created_at` | DateTime | Registration timestamp (UTC) |

**Relationships:**
- `ideas` → one-to-many with `Idea` (via `owner_id`)
- `nda_agreements` → one-to-many with `NDAAgreement` (via backref)
- `posts` → one-to-many with `Post` (via backref)

**Used by:** `routes/auth.py`, `routes/admin.py`, `routes/profile.py`, `routes/ideas.py`, all services.

---

### `models/idea.py` — Idea Model

**Purpose:** Stores a business idea with its three confidentiality layers.

**Class:** `Idea(db.Model)`

**Table columns:**

| Column | Type | Layer | Description |
|--------|------|-------|-------------|
| `id` | Integer PK | — | Auto-increment primary key |
| `owner_id` | Integer FK → User | — | Innovator who posted the idea |
| `title` | String(200) | 1 (Public) | Idea name |
| `sector` | String(100) | 1 (Public) | Industry sector |
| `country` | String(100) | 1 (Public) | Country of origin/market |
| `stage` | String(50) | 1 (Public) | Development stage |
| `teaser` | Text | 1 (Public) | Public-facing summary |
| `nda_preview` | Text | 2 (NDA) | Semi-confidential preview |
| `confidential_pitch` | Text | 3 (Full) | Full pitch details |
| `created_at` | DateTime | — | Posting timestamp (UTC) |

**Relationships:**
- `owner` → `User` (backpopulates `User.ideas`)
- `nda_agreements` → one-to-many with `NDAAgreement` (via backref)

**Used by:** `routes/ideas.py`, `routes/profile.py` (innovator profile).

---

### `models/nda.py` — NDA Agreement Model

**Purpose:** Records each digital NDA signature with forensic metadata.

**Class:** `NDAAgreement(db.Model)`

**Table columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | Auto-increment primary key |
| `idea_id` | Integer FK → Idea | Idea the NDA covers |
| `user_id` | Integer FK → User | Investor who signed |
| `accepted_at` | DateTime | Signature timestamp (UTC) |
| `ip_address` | String(45) | Signer's IP address (IPv4/IPv6) |
| `user_agent` | String(255) | Signer's browser/client string |

**Unique constraint:** `uq_nda_idea_user` on `(idea_id, user_id)` — prevents duplicate signatures.

**Relationships:**
- `idea` → `Idea` (backref `nda_agreements`)
- `user` → `User` (backref `nda_agreements`)

**Used by:** `routes/ideas.py`, `services/nda_service.py`.

---

### `models/post.py` — Post Model

**Purpose:** Represents community feed posts with granular visibility settings.

**Class:** `Post(db.Model)`

**Table columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | Auto-increment primary key |
| `author_id` | Integer FK → User | Post creator |
| `author_role` | String(20) | Cached role at time of posting |
| `title` | String(140) | Post headline |
| `content` | Text | Post body |
| `visibility` | String(30) | `"public"`, `"verified_only"`, `"investors_only"`, `"innovators_only"` |
| `created_at` | DateTime | Posting timestamp (UTC) |

**Relationships:**
- `author` → `User` (backref `posts`)

**Used by:** `routes/posts.py`.

---

### `models/logs.py` — Audit & Logging Models

**Purpose:** Provides three tables that together form a complete compliance and security audit trail.

#### `UserLoginLog`

Tracks every login attempt (successful or failed).

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | — |
| `user_id` | Integer FK → User | Attempting user |
| `success` | Boolean | True = authenticated, False = failed |
| `ip_address` | String(45) | Client IP |
| `user_agent` | String(255) | Client browser string |
| `failure_reason` | String(100) | e.g. `"wrong_password"`, `"user_not_found"` |
| `created_at` | DateTime | Event timestamp |

#### `IdeaViewLog`

Tracks every access to an idea at any confidentiality layer.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | — |
| `user_id` | Integer FK → User | Viewer (nullable for anonymous) |
| `idea_id` | Integer FK → Idea | Idea accessed |
| `action` | String(50) | `"view"`, `"open_confidential"`, `"request_nda"`, `"download"` |
| `ip_address` | String(45) | Client IP |
| `user_agent` | String(255) | Client browser string |
| `extra` | Text | Optional JSON extra data |
| `created_at` | DateTime | Event timestamp |

#### `AuditLog`

Generic log for sensitive administrative and business events.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | — |
| `actor_user_id` | Integer FK → User | User performing the action |
| `target_user_id` | Integer FK → User | User affected (e.g. KYC subject) |
| `idea_id` | Integer FK → Idea | Idea affected (if applicable) |
| `event_type` | String(80) | `"kyc_submitted"`, `"nda_signed"`, `"kyc_verified"`, etc. |
| `description` | Text | Human-readable summary |
| `metadata_json` | Text | JSON-serialised extra data (stored as text for SQLite compatibility) |
| `ip_address` | String(45) | Client IP |
| `user_agent` | String(255) | Client browser string |
| `created_at` | DateTime | Event timestamp |

**Used by:** `services/logging_service.py`.

---

## 7. Routes / Blueprints (`routes/`)

### `routes/__init__.py` — Package Marker

Contains a comment noting that all blueprints are registered in `app.py`'s `create_app()`. No executable code.

---

### `routes/auth.py` — Authentication Blueprint

**Blueprint name:** `auth_bp` | **URL prefix:** `/auth`

| Route | Methods | Description |
|-------|---------|-------------|
| `/auth/register` | GET, POST | Create a new account |
| `/auth/login` | GET, POST | Authenticate an existing user |
| `/auth/logout` | GET | End the current session |

**`/register` (GET/POST):**
- Collects: `first_name`, `last_name`, `email`, `password`, `role`, `id_type`, `id_number`.
- Validates email uniqueness (queries `User` by email).
- Hashes password with `generate_password_hash`.
- Creates `User` with `verification_status="pending"`.
- Redirects to `/auth/login` on success.
- Template: `register.html`

**`/login` (GET/POST):**
- Looks up `User` by email.
- Validates password with `check_password_hash`.
- Calls `log_login(user, success, failure_reason)` for both successful and failed attempts.
- Calls `login_user(user)` on success.
- Redirects to `/` on success.
- Template: `login.html`

**`/logout` (GET):**
- Calls `logout_user()`.
- Redirects to `/`.

---

### `routes/ideas.py` — Ideas Blueprint

**Blueprint name:** `ideas_bp` | **URL prefix:** `/ideas`

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/ideas/` | GET | No | Browse all ideas (public teasers) |
| `/ideas/<id>/public` | GET | No | Layer 1: teaser view |
| `/ideas/<id>/nda` | GET, POST | Yes (investor + KYC) | Layer 2: NDA gate |
| `/ideas/<id>/confidential` | GET | Yes (investor + KYC + NDA signed) | Layer 3: full pitch |

**`/ideas/` (GET):**
- Queries all `Idea` records, ordered descending.
- Template: `ideas_list.html`

**`/ideas/<id>/public` (GET):**
- Fetches idea by `id` (404 if not found).
- Calls `log_idea_view(idea_id, "public", viewer_id)`.
- Template: `idea_public.html`

**`/ideas/<id>/nda` (GET/POST):**
- Requires `@login_required`.
- Calls `can_view_nda_layer()` from `security_service`; returns 403 if denied (not an investor or KYC not verified).
- `GET`: Renders NDA confirmation form.
- `POST`: Calls `sign_nda(user_id, idea_id)` from `nda_service`; redirects to `/ideas/<id>/confidential`.
- Template: `idea_nda_confirm.html`

**`/ideas/<id>/confidential` (GET):**
- Requires `@login_required`.
- Calls `can_view_nda_layer()` → 403 if denied.
- Calls `has_signed_nda(user_id, idea_id)` from `nda_service` → 403 if not signed.
- Calls `log_idea_view(idea_id, "confidential", viewer_id)` for strong proof.
- Template: `idea_confidential.html`

---

### `routes/investor.py` — Investor Blueprint

**Blueprint name:** `investor_bp` | **URL prefix:** `/investor`

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/investor/dashboard` | GET | Yes (investor role) | Investor personal dashboard |

**`/investor/dashboard` (GET):**
- Requires `@login_required`.
- Returns HTTP 403 if `current_user.role != "investor"`.
- Currently a placeholder dashboard; future features include NDA history, viewed ideas, and reputation.
- Template: `investor_dashboard.html`

---

### `routes/admin.py` — Admin Blueprint

**Blueprint name:** `admin_bp` | **URL prefix:** `/admin`

**Local decorator:** `@admin_required` — checks `current_user.is_authenticated` and `current_user.role == "admin"`; returns HTTP 403 otherwise.

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/admin/kyc` | GET | Admin | List pending KYC submissions |
| `/admin/kyc/<user_id>/validate` | POST | Admin | Approve or reject KYC |

**`/admin/kyc` (GET):**
- Queries all `User` records with `verification_status == "pending"`.
- Template: `admin_kyc_list.html`

**`/admin/kyc/<user_id>/validate` (POST):**
- Reads form fields: `status` (`"verified"` or `"rejected"`) and `notes`.
- Sets `user.verification_status` directly to the submitted `status` value.
- Stores `notes` in `user.verification_notes`.
- Commits to database; flashes a success message.
- Redirects back to `/admin/kyc`.
- ⚠️ **Known issues:**
  1. The `status` value is accepted from form input without server-side validation — an admin could submit an arbitrary string beyond `"verified"` / `"rejected"`.
  2. The route updates `verification_status` but does **not** update the `kyc_verified` boolean field, leaving the two fields potentially out of sync.

---

### `routes/posts.py` — Posts Blueprint

**Blueprint name:** `posts_bp` | **URL prefix:** `/posts`

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/posts/` | GET | No | Community feed |
| `/posts/new` | GET, POST | Yes (investor/innovator) | Create a new post |

**`/posts/` (GET):**
- Queries 50 most recent `Post` records (`created_at DESC`).
- Template: `posts_feed.html`

**`/posts/new` (GET/POST):**
- Requires `@login_required` and role in `["investor", "innovator"]` (returns 403 otherwise).
- Validates `title` and `content` are non-empty.
- Creates `Post` with `author_id`, `author_role`, `title`, `content`, `visibility`.
- Commits; redirects to `/posts/`.
- Template: `post_new.html`

---

### `routes/profile.py` — Profile Blueprint

**Blueprint name:** `profile_bp` | **URL prefix:** `/profile`

**Helper functions:**

| Function | Description |
|----------|-------------|
| `_allowed_file(filename)` | Returns `True` if extension is in `{png, jpg, jpeg, gif, webp}` |
| `_get_upload_dir()` | Returns `/tmp/profile_pics` on Vercel; `static/uploads/profile_pics` locally |
| `_remove_old_picture(path)` | Deletes an existing profile picture file from disk |

| Route | Methods | Auth Required | Description |
|-------|---------|---------------|-------------|
| `/profile/<user_id>` | GET | No | View public profile |
| `/profile/edit` | GET, POST | Yes | Edit own profile |

**`/profile/<user_id>` (GET):**
- Fetches `User` by `user_id` (404 if not found).
- Passes user's ideas (if innovator) to template.
- Template: `profile_public.html`

**`/profile/edit` (GET/POST):**
- Requires `@login_required`.
- `GET`: Renders form pre-filled with current user data.
- `POST`:
  - Updates `first_name`, `last_name`, `bio`.
  - If a file is uploaded: validates extension, generates UUID filename, saves to upload directory, removes old picture, updates `profile_picture` path.
  - Commits; redirects to `/profile/<user_id>`.
- Template: `profile_edit.html`

---

## 8. Services (`services/`)

Services encapsulate business logic and are called by route handlers, keeping routes thin.

### `services/__init__.py` — Package Marker

Comment-only file. No executable code.

---

### `services/nda_service.py` — NDA Service

**Purpose:** All NDA-related database operations.

**Functions:**

#### `has_signed_nda(user_id: int, idea_id: int) -> bool`
- Queries `NDAAgreement` for a record matching `(user_id, idea_id)`.
- Returns `True` if found, `False` otherwise.
- **Used by:** `routes/ideas.py` (confidential layer gate).

#### `sign_nda(user_id: int, idea_id: int) -> None`
- Creates a new `NDAAgreement` record.
- Captures IP: reads `X-Forwarded-For` header first (for reverse-proxied deployments), falls back to `request.remote_addr`.
- Captures User-Agent string, truncated to 255 characters.
- Commits to database.
- **Used by:** `routes/ideas.py` (NDA POST handler).

---

### `services/security_service.py` — Security Service

**Purpose:** Centralised access control checks used as gates in route handlers.

**Functions:**

#### `is_verified_user() -> bool`
- Requires `current_user.is_authenticated`.
- Uses `getattr(current_user, "kyc_status", None)` to read a `kyc_status` attribute.
- If the attribute does not exist (returns `None`), returns `True` — this is an intentional **development fallback** that keeps the gate permissive while `kyc_status` is not yet defined on the `User` model.
- When `kyc_status` is present, returns `True` only if its value is `"approved"`.
- ⚠️ **Known security gap:** The current `User` model stores KYC state as `kyc_verified` (boolean) and `verification_status` (string), not `kyc_status`. Because `kyc_status` never exists on the model, `getattr` always returns `None` and the function always returns `True`. This means **the KYC verification gate is not enforced** — any authenticated investor can sign NDAs and access confidential content regardless of their actual verification status. This must be remediated before production use by changing the check to `current_user.kyc_verified == True` (or `current_user.verification_status == "verified"`).

#### `can_view_nda_layer() -> bool`
- Returns `True` only when **all three** conditions are met:
  1. `current_user.is_authenticated`
  2. `current_user.role == "investor"`
  3. `is_verified_user()` returns `True`
- **Used by:** `routes/ideas.py` (NDA and confidential layer gates).

---

### `services/kyc_service.py` — KYC Service

**Purpose:** KYC data submission and local format validation helpers.

**Functions:**

#### `submit_kyc(user, id_type, id_number, id_document_path) -> User`
- Updates the user's `id_type`, `id_number`, `id_document_path`.
- Sets `verification_status = "pending"`.
- Commits and returns the updated user.

#### `validate_id_format(id_type: str, id_number: str) -> tuple[bool, str | None]`
- Local (offline) format validation — not an external KYC API call.

| ID Type | Rule |
|---------|------|
| `"CIN"` / `"CNI"` | 5–10 chars; must contain both letters and digits |
| `"Passport"` | ≥ 6 chars; alphanumeric only |
| Other | ≥ 4 chars |

- Returns `(True, None)` if valid; `(False, error_message)` if invalid.

#### `mark_user_verified(user, notes) -> User`
- Sets `verification_status = "verified"`.
- Appends `notes` to `verification_notes`.
- Commits and returns the updated user.

**Note:** `admin.py` currently sets status directly without using `kyc_service`. These helpers are available for refactoring.

---

### `services/logging_service.py` — Logging Service

**Purpose:** Creates audit log entries for security and compliance.

**Functions:**

#### `log_login(user, success: bool, failure_reason: str | None = None) -> None`
- Creates a `UserLoginLog` record.
- Captures: `user_id`, `success`, `ip_address` (from `request`), `user_agent`, `failure_reason`.
- Commits to database.
- **Called by:** `routes/auth.py` login handler (both success and failure paths).

#### `log_idea_view(idea_id: int, viewed_layer: str, viewer_id: int | None = None) -> None`
- Creates an `IdeaViewLog` record only when `viewer_id` is not `None`.
- `viewed_layer` is stored as the `action` field (e.g. `"public"`, `"confidential"`).
- Captures: `user_id`, `idea_id`, `action`, `ip_address`, `user_agent`.
- Commits to database.
- **Called by:** `routes/ideas.py` public view and confidential view handlers.

---

## 9. Templates (`templates/`)

All templates extend `base.html` using Jinja2's `{% extends %}` / `{% block %}` mechanism.

### `base.html` — Master Layout

**Purpose:** Provides the shared HTML skeleton for every page.

**Structure:**
- `<!DOCTYPE html>` with `lang="fr"`.
- `<head>`: Bootstrap 5 CDN, link to `/static/css/style.css`, `{% block extra_styles %}`.
- **Navbar:**
  - Left: Brand logo / name linking to `/`.
  - Right (unauthenticated): Login, Register.
  - Right (authenticated): role-specific link (Investor Dashboard / Admin KYC), Posts, Profile, Logout.
- **Hero header:** Overridable `{% block hero %}` — displays mission statement by default.
- **Flash messages:** Bootstrap alert components for `success`, `danger`, `warning`, `info` categories.
- **Main content:** `{% block content %}`.
- **Footer:** Copyright, social links.
- Bootstrap 5 JS bundle CDN.

---

### `login.html` — Login Page

- **Extends:** `base.html`
- **Form fields:** Email, Password.
- **Action:** POST `/auth/login`
- **Links:** Registration page.

---

### `register.html` — Registration Page

- **Extends:** `base.html`
- **Form sections:**
  1. Account Info: First Name, Last Name, Email, Password, Role (dropdown: Innovator / Investor).
  2. KYC Identity Verification: ID Type (CIN / Passport / Other), ID Number, ID Document Scan (file upload, optional in MVP).
- **Action:** POST `/auth/register`

---

### `ideas_list.html` — Idea Browse Page

- **Extends:** `base.html`
- **Renders:** Responsive grid of idea cards.
- **Per-card:** Sector badge, Stage badge, Title, Teaser (truncated to 120 chars), Country, "See Idea" button → `/ideas/<id>/public`.

---

### `idea_public.html` — Public Teaser (Layer 1)

- **Extends:** `base.html`
- **Renders:** Full teaser, metadata (sector, stage, country), NDA protection notice.
- **Conditional CTA:**
  - Authenticated investor → "Access (NDA)" button → `/ideas/<id>/nda`.
  - Not authenticated → "Login to access" button.

---

### `idea_nda_confirm.html` — NDA Confirmation (Layer 2 Gate)

- **Extends:** `base.html`
- **Content:** NDA summary (non-disclosure, no copy, no transmission, liability notice), access logging notice.
- **Actions:**
  - Accept (form POST `/ideas/<id>/nda`) → proceeds to Layer 3.
  - Cancel → back to public teaser.

---

### `idea_confidential.html` — Confidential Pitch (Layer 3)

- **Extends:** `base.html`
- **Content:** Access warning ("this access is timestamped"), NDA Preview section, Full Confidential Pitch section.
- **Back button** → returns to idea list.

---

### `investor_dashboard.html` — Investor Dashboard

- **Extends:** `base.html`
- **Content:** Welcome greeting with user's first name; placeholder text describing planned features (NDA history, viewed ideas, reputation score).

---

### `posts_feed.html` — Community Feed

- **Extends:** `base.html`
- **Header:** Title, description, "New Post" CTA (visible to authenticated investors and innovators).
- **Feed:** Grid of post cards showing: author role badge, timestamp, visibility badge, title, content excerpt, author name.

---

### `post_new.html` — Create Post

- **Extends:** `base.html`
- **Form fields:** Title (max 140 chars), Content (textarea), Visibility (dropdown).
- **Actions:** Publish (POST `/posts/new`), Cancel.

---

### `admin_kyc_list.html` — Admin KYC Panel

- **Extends:** `base.html`
- **Content:** Table of users with `verification_status == "pending"`.
- **Columns:** ID, Name, Email, Role, ID Type, ID Number, Actions.
- **Actions per row:**
  - "Valider" (green) → POST `/admin/kyc/<id>/validate` with `status=verified`.
  - "Rejeter" (red) → POST `/admin/kyc/<id>/validate` with `status=rejected`.
- **Empty state:** "No pending users" message.

---

### `profile_public.html` — Public Profile

- **Extends:** `base.html`
- **Content:**
  - Profile picture (circular image or gradient placeholder with initials).
  - Full name, Role badge, KYC verified badge (if applicable).
  - Bio ("About" section).
  - Email (only visible to the profile owner).
  - Member since date.
  - For innovators: list of their published ideas with links.
  - "Edit profile" button (only visible to profile owner).

---

### `profile_edit.html` — Edit Profile

- **Extends:** `base.html`
- **Form sections:**
  - Profile picture upload with format hint (PNG, JPG, GIF, WebP, max 2 MB).
  - First Name and Last Name fields (pre-filled, required).
  - Bio textarea (pre-filled).
- **Actions:** Save (POST `/profile/edit`), Cancel.

---

## 10. Static Assets (`static/`)

### `static/css/style.css` — Custom Design System

**Purpose:** Provides all custom visual styling on top of Bootstrap 5.

**CSS Custom Properties (Design Tokens):**

| Variable | Value | Use |
|----------|-------|-----|
| `--bg` | `#f1f5f9` | Page background |
| `--surface` | `#ffffff` | Card / container background |
| `--ink` | `#0f172a` | Primary text |
| `--muted` | `#475569` | Secondary text |
| `--muted-2` | `#64748b` | Tertiary text |
| `--brand` | `#1e3a8a` | Primary brand blue |
| `--brand-2` | `#2563eb` | Secondary / interactive blue |
| `--brand-soft` | `#eff6ff` | Light blue accent background |
| `--line` | `#e2e8f0` | Border colour |
| `--radius` | `12px` | Default border radius |
| `--radius-lg` | `16px` | Large border radius |
| `--shadow` | box-shadow | Subtle card shadow |
| `--shadow-2` | box-shadow | Elevated card shadow |

**Key component classes:**

| Class | Description |
|-------|-------------|
| `.section` | Main content container with white background, padding, and shadow |
| `.idea-card` | Idea grid card with hover lift and border highlight effect |
| `.idea-tag` | Pill-shaped badge for sector / stage / country |
| `.card-glass` | General card styling |
| `.profile-avatar` | Circular profile image (80×80 px) |
| `.profile-avatar-placeholder` | Gradient placeholder showing initials |
| `.btn-primary` / `.btn-secondary` | Custom button overrides |
| `.nda-box` | Light gray highlighted box for NDA text |

**Typography:**
- Font family: Inter (system fallback stack).
- Base size: 15px, line-height 1.65.

**Responsive behaviour:** Media queries adjust padding and font size for mobile viewports.

---

### `static/uploads/` — User Upload Storage

| Path | Description |
|------|-------------|
| `static/uploads/logo.jpeg` | Platform logo shown in the navbar |
| `static/uploads/profile_pics/.gitkeep` | Placeholder keeping the directory in git; actual uploads are git-ignored |

On Vercel, profile picture uploads are redirected to `/tmp/profile_pics/` because the Vercel filesystem is read-only outside `/tmp`.

---

## 11. Data Flow & Key Workflows

### User Registration & KYC

```
User fills /auth/register
  → User record created (verification_status = "pending")
  → Admin logs in, visits /admin/kyc
  → Admin clicks Validate → verification_status = "verified", kyc_verified = True
  → User can now sign NDAs and access confidential content
```

### Three-Layer Idea Access

```
Anyone visits /ideas/
  → Sees public teasers (Layer 1 cards)

Anyone visits /ideas/<id>/public
  → log_idea_view(idea_id, "public", viewer_id)
  → Reads teaser, sector, stage, country

Authenticated investor (KYC verified) visits /ideas/<id>/nda
  → security_service.can_view_nda_layer() → True
  → Sees NDA agreement text
  → POST to /ideas/<id>/nda
    → nda_service.sign_nda(user_id, idea_id) creates NDAAgreement with IP + user_agent

Investor visits /ideas/<id>/confidential
  → can_view_nda_layer() → True
  → nda_service.has_signed_nda(user_id, idea_id) → True
  → log_idea_view(idea_id, "confidential", viewer_id)
  → Reads nda_preview + confidential_pitch
```

### Audit Trail

Every sensitive action produces a database record:

| Action | Log table | Service function |
|--------|-----------|-----------------|
| Successful login | `UserLoginLog` | `log_login(user, True)` |
| Failed login | `UserLoginLog` | `log_login(user, False, reason)` |
| Public idea view | `IdeaViewLog` | `log_idea_view(id, "public", uid)` |
| Confidential idea view | `IdeaViewLog` | `log_idea_view(id, "confidential", uid)` |
| NDA signed | `NDAAgreement` | `sign_nda(user_id, idea_id)` |

---

## 12. Security Architecture

| Concern | Mechanism |
|---------|-----------|
| Password storage | Werkzeug `generate_password_hash` / `check_password_hash` (PBKDF2-HMAC-SHA256) |
| Session management | Flask-Login signed cookies (`SECRET_KEY`) |
| Access control | `@login_required` decorator + manual role checks in route handlers |
| KYC gating | `security_service.can_view_nda_layer()` checks role and `kyc_verified` flag |
| NDA gating | `nda_service.has_signed_nda()` check before confidential layer |
| File upload safety | `werkzeug.utils.secure_filename` + allowlist of extensions + UUID filenames |
| IP capture | `X-Forwarded-For` header (reverse proxy) falling back to `remote_addr` |
| Upload size limit | `MAX_CONTENT_LENGTH = 2 MB` in Flask config |
| Audit trail | Immutable log tables for logins, idea views, and admin decisions |
| Secret key | Environment variable in production; hard-coded dev fallback (must be changed) |

---

## 13. Deployment Architecture

```
Internet → Vercel Edge Network
             │
             ├── /static/* → Static CDN (CSS, images)
             │
             └── /* → api/index.py (Python Serverless Function)
                           │
                           └── Flask app (create_app())
                                  │
                                  ├── SQLite (/tmp/ideas2invest.db) ← dev/Vercel
                                  └── PostgreSQL (DATABASE_URL env) ← production
```

**Vercel constraints handled:**
- Filesystem is read-only except `/tmp` → SQLite and profile uploads use `/tmp`.
- Cold starts → `db.create_all()` in `api/index.py` ensures tables exist.
- No persistent disk → profile pictures in `/tmp` are ephemeral; a persistent storage service (S3, Cloudinary) would be needed for production reliability.

**Environment variables required for production:**

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session signing key |
| `DATABASE_URL` | PostgreSQL connection string |
| `VERCEL` | Set automatically by Vercel runtime; triggers `/tmp` path logic |
