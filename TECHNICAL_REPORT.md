# Collabry Technical Report

## Overview

Collabry is a Flask marketplace owned by Viral Talent. It connects verified influencers and businesses through creator media kits, campaign briefs, deterministic match scoring, collaboration requests, and proof-based account verification.

## Architecture

- `app.py`: Flask application factory, blueprint registration, home route, and guarded demo seeding when `COLLABRY_DEMO=1`.
- `models/`: SQLAlchemy models for users, creator profiles, campaigns, collaboration agreements, collaboration requests, and audit logs.
- `routes/`: Blueprints for auth, creators, campaigns, business dashboard, influencer dashboard, admin verification, and public profile editing.
- `services/`: Matching, collaboration agreement handling, verification helpers, demo seeding, and audit/view logging.
- `templates/`: Jinja2 marketplace interface.
- `static/css/style.css`: Custom Collabry design system.
- `api/index.py`: Vercel serverless entry point.

## Core Models

| Model | Purpose |
|---|---|
| `User` | Account identity, role, verification status, public bio |
| `CreatorProfile` | Influencer media kit, public summary, protected collaboration details |
| `Campaign` | Business campaign brief and target criteria |
| `CollaborationRequest` | Business invite or influencer application |
| `CollaborationAgreement` | Business acceptance record before protected creator access |
| `CreatorViewLog` / `AuditLog` | Marketplace access and sensitive-action trail |

## Main Workflows

1. Influencer registers with identity proof and a public social profile, then creates a creator media kit at `/creators/onboarding`.
2. Business registers with company proof, then posts a campaign at `/campaigns/new` after admin approval.
3. Collabry scores creator/campaign fit by niche, platform overlap, country match, budget compatibility, engagement, and follower signals.
4. Influencer applies to a campaign through `/campaigns/<id>/apply`.
5. Business invites creators from `/creators/<id>/invite`.
6. Verified businesses accept `/creators/<id>/agreement` before viewing `/creators/<id>/media-kit`.

## Verification

- Registration requires a proof upload for both roles.
- Creator accounts submit legal ID proof and a public social profile URL.
- Business accounts submit company name plus registration, tax, or equivalent company proof.
- Proof files are stored outside public static paths under `instance/verification_docs` locally.
- Admins review pending users at `/admin/verification` and open proof files through an admin-only route.
- Pending businesses cannot post campaigns, invite creators, or unlock protected media-kit details.
- Pending creators do not appear in discovery and cannot apply to campaigns.

## Local Development

```bash
pip install -r requirements.txt
COLLABRY_DEMO=1 python app.py
```

The app runs at `http://127.0.0.1:5000`.

## Deployment

The existing Vercel setup remains unchanged:

- `api/index.py` imports `create_app()` and creates tables at startup.
- `vercel.json` routes static assets from `/static/*` and all app requests to the Python serverless entry.
- `DATABASE_URL` can override local SQLite for production.
