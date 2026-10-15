# Database

Preferred: Turso / libSQL via sqlalchemy-libsql or the libsql Python package.

Local development fallback: `sqlite:///local.db`

Migrations: Flask-Migrate (Alembic).

Critical tables: users, delivery_identity_slots (exactly 2 rows), food_items, option_groups, orders, order_items, payments, qr_submissions, cod_collections, idempotency_keys, audit_logs.

Never seed fictional production orders or reviews.
