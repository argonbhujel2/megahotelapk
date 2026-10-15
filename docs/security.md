# Security Notes

- Passwords hashed with Werkzeug (scrypt/pbkdf2).
- JWT access + refresh with rotation/revocation support via Session table.
- Role never accepted from client; always read from JWT claims issued by backend.
- Guest tracking uses cryptographically unguessable tokens.
- Idempotency keys prevent duplicate order creation.
- Inventory changes occur inside database transactions.
- Rate limiting on login and general endpoints.
- No secrets in Flutter source or committed files.
- AuditLog model for privileged actions.
- Account deletion request support (implementation points provided).
