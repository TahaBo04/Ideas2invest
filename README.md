# Ideas2invest

> **A B2B web platform connecting innovators with investors through a structured, confidentiality-first deal flow.**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-black?logo=flask)](https://flask.palletsprojects.com/)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel)](https://vercel.com/)

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [How It Works — Platform Workflow](#how-it-works--platform-workflow)
  - [1. Registration & KYC Verification](#1-registration--kyc-verification)
  - [2. Innovator Posts an Idea](#2-innovator-posts-an-idea)
  - [3. The Three-Layer Confidentiality System](#3-the-three-layer-confidentiality-system)
  - [4. NDA Signing Flow](#4-nda-signing-flow)
  - [5. Community Feed (Posts)](#5-community-feed-posts)
  - [6. Admin Panel](#6-admin-panel)
- [Roles](#roles)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Deployment (Vercel)](#deployment-vercel)
- [Security & Audit Trail](#security--audit-trail)

---

## About the Project

**Ideas2invest** is a B2B web platform designed to bridge the gap between innovators with promising business ideas and investors looking for opportunities. The platform's defining feature is its **three-layer idea confidentiality system**, which lets innovators share just enough information to attract interest — without exposing sensitive details until a formal NDA is in place.

All users must pass a **KYC (Know Your Customer)** verification process before accessing protected content, ensuring a trusted and accountable ecosystem.

---

## Key Features

- 🔐 **Three-layer idea confidentiality** — public teaser → NDA-gated preview → full confidential pitch
- ✅ **KYC verification** — identity verification for all users before accessing sensitive content
- 📝 **Digital NDA signing** — investors sign NDAs in-platform with IP & user-agent logging as proof
- 👥 **Role-based access control** — separate workflows for `innovator`, `investor`, and `admin`
- 📣 **Community feed** — visibility-controlled posts for sharing updates and insights
- 🕵️ **Full audit trail** — every login, idea view, and NDA signature is logged
- 🚀 **Serverless deployment** — runs on Vercel with zero-config

---

## How It Works — Platform Workflow

### 1. Registration & KYC Verification

1. A new user visits `/auth/register` and chooses a role: **Innovator** or **Investor**.
2. They provide their name, email, password, and identity document details (e.g., CIN or Passport number).
3. Upon registration, their account is created with `verification_status = "pending"`.
4. An **Admin** reviews the submission at `/admin/kyc` and approves or rejects the KYC request.
5. Only **verified** users can access NDA-protected or confidential idea content.

```
Register → Pending KYC → Admin Review → Verified ✅ (or Rejected ❌)
```

---

### 2. Innovator Posts an Idea

Once verified, an innovator can submit a business idea structured across **three confidentiality layers**:

| Layer | Field | Visibility |
|---|---|---|
| **Layer 1** | `teaser` | Public — anyone can read |
| **Layer 2** | `nda_preview` | Investors who sign the NDA |
| **Layer 3** | `confidential_pitch` | Investors who have already signed the NDA |

The idea also includes metadata: `title`, `sector`, `country`, and `stage`.

---

### 3. The Three-Layer Confidentiality System

#### 🟢 Layer 1 — Public Teaser (`/ideas/<id>/public`)
- Visible to **everyone**, including unauthenticated visitors.
- Shows the idea title, sector, country, stage, and teaser description.
- Every view is logged with the viewer's ID (if authenticated).

#### 🟡 Layer 2 — NDA Gate (`/ideas/<id>/nda`)
- Requires the viewer to be **authenticated**, have the **investor** role, and be **KYC-verified**.
- If all conditions are met, the investor is presented with an NDA agreement to accept.
- Once accepted, they are redirected to the confidential layer.

#### 🔴 Layer 3 — Confidential Pitch (`/ideas/<id>/confidential`)
- Only accessible to investors who have **already signed the NDA** for this specific idea.
- Every access to this layer is logged as a "confidential" view event.

```
Public Teaser
    └─► [Investor + KYC] ──► NDA Confirmation Page
                                    └─► [Sign NDA] ──► Full Confidential Pitch
```

---

### 4. NDA Signing Flow

When an investor accepts the NDA:
1. A `NDAAgreement` record is created in the database, uniquely keyed on `(idea_id, user_id)`.
2. The investor's **IP address** and **User-Agent** are stored as proof of digital consent.
3. The constraint `uq_nda_idea_user` ensures an investor can only sign each NDA once.
4. All NDA events are recorded in the `AuditLog`.

---

### 5. Community Feed (Posts)

- Located at `/posts/`, the feed shows the latest 50 posts.
- **Innovators** and **Investors** can publish posts at `/posts/new`.
- Each post has a `visibility` setting:
  - `public` — visible to all
  - `verified_only` — only KYC-verified users
  - `investors_only` — only investors
  - `innovators_only` — only innovators

---

### 6. Admin Panel

Accessible at `/admin/kyc` (admin role required).

- View all users with `verification_status = "pending"`.
- Approve or reject each user's KYC, optionally adding notes.
- Status options: `pending`, `verified`, `rejected`.

---

## Roles

| Role | Capabilities |
|---|---|
| `innovator` | Register, post ideas (all three layers), publish posts, manage profile |
| `investor` | Register, browse ideas, sign NDAs, access confidential pitches (after KYC), publish posts |
| `admin` | Review & approve/reject KYC submissions for all users |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Flask 3.0.2 |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Database | SQLite (local) / PostgreSQL (production) |
| Authentication | Flask-Login 0.6.3 + Werkzeug password hashing |
| Templating | Jinja2 3.1.3 |
| Production Server | Gunicorn 22.0.0 |
| Deployment | Vercel (serverless Python) |

---

## Project Structure

```
Ideas2invest/
├── app.py                  # Flask application factory (create_app)
├── config.py               # Configuration class, Vercel detection
├── extensions.py           # Shared extensions: db, login_manager
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel routing & build config
├── api/
│   └── index.py            # Vercel serverless entry point
├── models/
│   ├── user.py             # User model (roles, KYC fields)
│   ├── idea.py             # Idea model (3-layer confidentiality)
│   ├── nda.py              # NDAAgreement model
│   ├── post.py             # Post model (community feed)
│   └── logs.py             # UserLoginLog, IdeaViewLog, AuditLog
├── routes/
│   ├── auth.py             # /auth — register, login, logout
│   ├── ideas.py            # /ideas — idea listing + 3-layer views
│   ├── investor.py         # /investor — investor dashboard
│   ├── admin.py            # /admin — KYC management
│   ├── posts.py            # /posts — community feed
│   └── profile.py          # /profile — public profile + edit
├── services/
│   ├── nda_service.py      # NDA signing & verification logic
│   ├── security_service.py # Role & KYC access checks
│   ├── kyc_service.py      # KYC submission & validation helpers
│   └── logging_service.py  # Login & idea view audit logging
├── templates/              # Jinja2 HTML templates
└── static/
    ├── css/                # Custom stylesheets
    └── uploads/            # User-uploaded files (profile pictures)
```

---

## Getting Started

### Prerequisites

- Python 3.12
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/TahaBo04/Ideas2invest.git
cd Ideas2invest

# 2. (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the development server
python app.py
```

The app will be available at **http://127.0.0.1:5000** with debug mode enabled.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string (production) | Uses SQLite locally |
| `SECRET_KEY` | Flask session secret key | Set in `config.py` |
| `VERCEL` | Set automatically by Vercel to enable `/tmp` paths | — |

> ⚠️ Never commit `.env` files or `.db` database files.

---

## Deployment (Vercel)

The project is pre-configured for **Vercel serverless deployment**:

- `api/index.py` — exports the Flask app as a Vercel serverless function.
- `vercel.json` — routes all traffic to the serverless handler.
- `config.py` — detects the `VERCEL` environment variable and switches the SQLite path to `/tmp` (the only writable directory on Vercel). File uploads also target `/tmp`.

To deploy:

```bash
vercel deploy
```

---

## Security & Audit Trail

Ideas2invest takes data integrity and accountability seriously:

- **Passwords** are hashed using Werkzeug's `generate_password_hash` / `check_password_hash` (PBKDF2).
- **Every login attempt** (success or failure) is recorded in `UserLoginLog` with IP address and failure reason.
- **Every idea view** (public or confidential) is recorded in `IdeaViewLog`.
- **Every NDA signature** stores the investor's IP address and User-Agent as legal proof of digital consent.
- **Generic sensitive actions** (KYC approvals, idea changes) are recorded in `AuditLog` with `event_type` and a human-readable description.
- **Role + KYC checks** are enforced at the service layer (`security_service.py`) before any protected content is served.

---

*Built with Flask · Deployed on Vercel*