"""One-time Admin bootstrap and fixed delivery identity slots."""
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.delivery import DeliveryIdentitySlot
from werkzeug.security import check_password_hash


def ensure_admin_bootstrap():
    """Create the initial Admin account from environment variables if enabled and no admin exists."""
    if not current_app.config.get("ADMIN_BOOTSTRAP_ENABLED"):
        return

    existing = User.query.filter_by(role="admin").first()
    if existing:
        return

    username = current_app.config.get("ADMIN_USERNAME")
    password_hash = current_app.config.get("ADMIN_PASSWORD_HASH")
    if not username or not password_hash:
        current_app.logger.warning("Admin bootstrap enabled but ADMIN_USERNAME or ADMIN_PASSWORD_HASH missing")
        return

    admin = User(
        email=username,
        password_hash=password_hash,
        full_name="System Administrator",
        role="admin",
        is_active=True,
    )
    db.session.add(admin)

    # Ensure exactly two delivery identity slots exist
    for slot_id in (1, 2):
        slot = DeliveryIdentitySlot.query.get(slot_id)
        if not slot:
            db.session.add(DeliveryIdentitySlot(id=slot_id, display_name=None))

    try:
        db.session.commit()
        current_app.logger.info("Admin bootstrap completed for %s", username)
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("Admin bootstrap failed: %s", exc)


def ensure_delivery_slots():
    """Guarantee exactly two slots exist. Never create a third."""
    for slot_id in (1, 2):
        if not DeliveryIdentitySlot.query.get(slot_id):
            db.session.add(DeliveryIdentitySlot(id=slot_id))
    db.session.commit()
