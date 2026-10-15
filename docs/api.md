# API Overview (v1)

Base: `/api/v1`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | — | Shared login |
| POST | /auth/guest | — | Guest entry |
| POST | /auth/refresh | refresh | New access token |
| GET  | /auth/me | access | Current user |
| GET  | /menu/categories | — | Categories |
| GET  | /menu/foods | — | Food list + filters |
| GET  | /menu/foods/:id | — | Food detail + options |
| POST | /orders | optional | Create order (idempotent) |
| GET  | /orders/track/:token | — | Secure guest tracking |
| PATCH| /orders/:id/status | admin/staff | Status transition |
| GET  | /admin/dashboard | admin | Operational counts |
| GET  | /admin/delivery-slots | admin | Two slots |
| PATCH| /admin/delivery-slots/:id | admin | Edit slot name (1 or 2 only) |
| POST | /payments/qr/submit | — | Submit QR reference |
| POST | /payments/qr/:id/verify | admin/staff | Approve/reject |
| POST | /staff/cod-collect/:order_id | staff | Mark COD collected |
| POST | /staff/location | staff | Real location update |
| GET  | /config | — | App config + min version |
| GET  | /banners | — | Active banners |
| POST | /support/tickets | — | Create support ticket |

All mutating endpoints validate state and permissions server-side.
