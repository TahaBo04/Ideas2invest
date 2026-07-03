# Collabry

> A Viral Talent web app that connects influencers with businesses looking for performance-driven creator ads.

Collabry is a Flask marketplace for campaign discovery, creator media kits, smart match scoring, and protected collaboration access. Businesses can post campaign briefs and invite creators. Influencers can build a media kit, browse campaigns, and apply when the audience fit is strong.

## Features

- Creator profiles with niche, platforms, audience country, followers, engagement rate, starting rate, public media-kit summary, and protected collaboration details.
- Business campaign briefs with target niche, platforms, country, budget range, goal, brief, and deliverables.
- Deterministic smart match scoring with no external AI/API key.
- Collaboration requests for both business invites and influencer applications.
- Collaboration agreement gate before businesses can view protected creator details.
- Admin verification queue with private proof-document review for marketplace trust.
- Guarded local demo seeding with sample creators, campaigns, and accounts.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Flask 3.0.2 |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Database | SQLite locally, PostgreSQL through `DATABASE_URL` in production |
| Authentication | Flask-Login + Werkzeug password hashing |
| Frontend | Jinja2, Bootstrap bundle, custom CSS |
| Deployment | Vercel Python serverless entry at `api/index.py` |

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start with demo data
COLLABRY_DEMO=1 python app.py
```

Open `http://127.0.0.1:5000`.

Demo account password: `collabry123`.

Useful demo emails:

- `brand@collabry.local`
- `lina@collabry.local`
- `samir@collabry.local`
- `nora@collabry.local`
- `admin@collabry.local`

## Main Routes

- `/auth/register`, `/auth/login`
- `/creators/`, `/creators/onboarding`, `/creators/<id>`, `/creators/<id>/agreement`, `/creators/<id>/media-kit`
- `/campaigns/`, `/campaigns/new`, `/campaigns/<id>`, `/campaigns/<id>/apply`
- `/business/dashboard`, `/influencer/dashboard`, `/admin/verification`

## Notes

- `COLLABRY_DEMO=1` is required for demo seeding. Production does not seed automatically.
- Local SQLite uses `collabry.db`, which is ignored by git.
- User uploads in `static/uploads/profile_pics/` are ignored except `.gitkeep`.
- Verification proof uploads are stored privately under `instance/verification_docs` locally and can only be opened through the admin review route.
- Businesses must submit legal company proof; creators must submit identity proof plus a public social profile before Viral Talent can approve them.
