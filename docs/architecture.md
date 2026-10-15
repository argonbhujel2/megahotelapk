# Architecture

## High-level

```
[Flutter Android App]
        |
        | HTTPS JSON
        v
[Flask REST API  /api/v1/...]
        |
        v
[Turso / libSQL]
        +
[Cloudinary]  (media URLs only)
```

## Roles

- **Customer** — browse, order, track, review, support
- **Guest** — same as customer for ordering; secure tracking token; no history of other users
- **Staff** — assigned deliveries, location sharing, COD collection (if permitted), limited QR verify
- **Admin** — full operations, menu, branding, two delivery identity slots, reports

Role is determined exclusively by the backend after authentication. The Flutter client never decides authorization.

## Delivery Identities

Exactly two fixed slots (`delivery_identity_slots.id = 1 | 2`).  
Admin may edit `display_name`. No endpoint allows creation of a third slot.

## Order Lifecycle

```
New → Accepted → Preparing → Ready for Delivery → Assigned → Out for Delivery → Delivered
```

Payment status is independent (`pending | submitted | verified | collected | rejected | refunded`).

## Money

All monetary values use `Decimal` / `Numeric(12,2)` on the backend. Client-supplied prices are ignored.
