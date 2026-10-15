# Mega Hotel — Restaurant Ordering & Delivery Application

**Production-oriented Flutter Android + Python Flask + Turso/libSQL system**

Official product name: **Mega Hotel**  
Developer credit: Engineered by BAM Studio — https://bamstudio.argan.com.np/

## Architecture Overview

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Mobile             | Flutter (Material 3), Dart          |
| Backend            | Python 3.12, Flask, SQLAlchemy      |
| Database           | Turso / libSQL (SQLite-compatible)  |
| Media              | Cloudinary                          |
| Auth               | JWT + refresh tokens, OAuth hooks   |
| Localization       | English + Nepali                    |
| Currency           | NPR (decimal-safe)                  |

One Android application contains Customer, Admin and Staff experiences with role-based routing determined by the backend.

## Critical Isolation Rule

This project is completely independent of any existing Mega Hotel website or hotel management system.  
It uses its own database, credentials and deployment configuration.

## Quick Start (Windows PowerShell)

See `docs/deployment.md` and `docs/android-build.md` for full instructions.

```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # edit with your values
flask db upgrade
python -m flask run

# Mobile (requires Flutter SDK on your machine)
cd mobile
flutter pub get
flutter run
```

## Project Structure

```
mega_hotel_delivery/
├── README.md
├── .gitignore
├── .env.example
├── docs/                  # Architecture, API, security, deployment, testing
├── backend/               # Flask REST API
│   ├── app/
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
├── mobile/                # Flutter Android application
│   ├── lib/
│   ├── assets/
│   └── pubspec.yaml
└── scripts/               # Helper scripts
```

## Key Features Implemented in Source

- Shared login with role determination by backend
- Guest ordering + secure unguessable tracking tokens
- Exactly two fixed delivery identity slots (Admin-editable names only)
- COD + QR payment flows (payment status independent of order status)
- Required / optional customization groups + multiple extras
- Inventory with concurrency-safe reservation
- English / Nepali localization scaffolding
- Admin & Staff dashboards inside the same Flutter app
- Cloudinary integration points
- Turso/libSQL configuration with local SQLite fallback for development
- Idempotency keys for order creation
- Audit logging hooks
- Minimum app version enforcement hooks

## External Credentials Required

You must supply (never commit real values):

- `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN`
- `CLOUDINARY_*`
- Google / Facebook OAuth client IDs & secrets
- Push notification provider keys
- Map provider API key (if used)
- Admin bootstrap password hash

See `.env.example` and `docs/deployment.md`.

## License

Proprietary — Mega Hotel / BAM Studio. All rights reserved.
