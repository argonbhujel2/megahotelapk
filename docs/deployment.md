# Deployment Guide — Mega Hotel Delivery

## Prerequisites

- Python 3.12+
- Flutter 3.16+ (on the developer machine)
- Turso account + database
- Cloudinary account
- (Optional) Google / Facebook developer consoles for OAuth

## Backend (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example .env
# Edit .env with real values
# Generate admin password hash:
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('YourStrongPasswordHere'))"
# Put the hash into ADMIN_PASSWORD_HASH and set ADMIN_BOOTSTRAP_ENABLED=true

# Local SQLite (development)
# DATABASE_URL=sqlite:///local.db

# Turso (production)
# TURSO_DATABASE_URL=libsql://...
# TURSO_AUTH_TOKEN=...
# DATABASE_URL=sqlite+libsql://...?secure=true

flask db init   # first time only
flask db migrate -m "initial"
flask db upgrade
python -m flask run --host=0.0.0.0 --port=5000
```

### Production WSGI

```powershell
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

Vercel / other serverless platforms: confirm current Flask + libsql/sqlalchemy-libsql compatibility before deploying. Prefer a conventional VPS or container if the platform does not support the required long-lived connections or dialect.

## Mobile

```powershell
cd mobile
flutter pub get
# Debug
flutter run
# Release APK (requires signing config)
flutter build apk --release --dart-define=API_BASE_URL=https://your-api.example.com
# App Bundle for Play Store
flutter build appbundle --release --dart-define=API_BASE_URL=https://your-api.example.com
```

## Environment Isolation

- Never point this application at the existing Mega Hotel production database.
- Use a dedicated Turso database and Cloudinary folder.
- Keep `.env` out of version control.

## Known Limitations in This Environment

- Flutter SDK and Android SDK are not present in the build environment that packaged this ZIP.
- APK/AAB must be built on a machine that has the Flutter toolchain installed.
- Real Google/Facebook OAuth, Cloudinary uploads, push notifications and live map tiles require external credentials that are intentionally not included.
