"""Exactly two fixed delivery identity slots."""
from datetime import datetime
from app.extensions import db
import uuid


class DeliveryIdentitySlot(db.Model):
    """
    Fixed two-slot delivery identity system.
    Admin may only edit the display name of the two existing slots.
    No additional slots may ever be created.
    """
    __tablename__ = "delivery_identity_slots"

    id = db.Column(db.Integer, primary_key=True)  # 1 or 2 only
    display_name = db.Column(db.String(100), nullable=True)  # null until Admin configures
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(36), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "display_name": self.display_name or f"Delivery Staff {self.id}",
            "is_active": self.is_active,
            "configured": self.display_name is not None,
        }
