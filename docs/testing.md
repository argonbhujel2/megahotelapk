# Testing

## Backend (available in this environment)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

Tests cover:
- Health endpoint
- Invalid login
- Guest entry
- Exactly two delivery identity slots
- Rejection of non-COD/QR payment methods

## Flutter

Requires Flutter SDK on the developer machine:

```powershell
cd mobile
flutter test
```

## Integration

Run backend against a non-production Turso or local SQLite database and exercise the Flutter app against that API.
