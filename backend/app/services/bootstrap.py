"""Bootstrap the Mega Hotel admin account."""
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.delivery import DeliveryIdentitySlot
from werkzeug.security import generate_password_hash


def ensure_admin_bootstrap():
    if not current_app.config.get("ADMIN_BOOTSTRAP_ENABLED"):
        return

    username = "admin@megahotel"
    password = "megahotel@123"

    try:
        admins = User.query.filter_by(role="admin").all()
        admin = next(
            (u for u in admins if u.email == username),
            admins[0] if admins else None,
        )

        existing = User.query.filter_by(email=username).first()
        if existing and existing.role != "admin":
            current_app.logger.error(
                "Target email belongs to a non-admin account."
            )
            return

        if admin is None:
            admin = User(
                email=username,
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            db.session.add(admin)

        admin.email = username
        admin.password_hash = generate_password_hash(password)
        admin.role = "admin"
        admin.is_active = True

        for other in admins:
            if other.id != admin.id:
                other.is_active = False

        for slot_id in (1, 2):
            if db.session.get(DeliveryIdentitySlot, slot_id) is None:
                db.session.add(
                    DeliveryIdentitySlot(id=slot_id, display_name=None)
                )

        db.session.commit()
        current_app.logger.info("Admin bootstrap completed.")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Admin bootstrap failed.")


def ensure_delivery_slots():
    for slot_id in (1, 2):
        if db.session.get(DeliveryIdentitySlot, slot_id) is None:
            db.session.add(DeliveryIdentitySlot(id=slot_id))
    db.session.commit()
