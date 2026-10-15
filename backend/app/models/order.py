"""Orders, items, delivery and location tracking."""
from datetime import datetime
from decimal import Decimal
from app.extensions import db
import uuid
import secrets


ORDER_STATUSES = (
    "new",
    "accepted",
    "preparing",
    "ready_for_delivery",
    "assigned",
    "out_for_delivery",
    "delivered",
    "cancelled",
    "rejected",
)

VALID_TRANSITIONS = {
    "new": {"accepted", "rejected", "cancelled"},
    "accepted": {"preparing", "cancelled"},
    "preparing": {"ready_for_delivery", "cancelled"},
    "ready_for_delivery": {"assigned", "cancelled"},
    "assigned": {"out_for_delivery", "cancelled"},
    "out_for_delivery": {"delivered", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
    "rejected": set(),
}


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    tracking_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)  # null for guests
    is_guest = db.Column(db.Boolean, default=False)
    guest_name = db.Column(db.String(150), nullable=True)
    guest_phone = db.Column(db.String(30), nullable=True)

    status = db.Column(db.String(30), default="new", nullable=False, index=True)
    payment_status = db.Column(db.String(30), default="pending")  # pending | paid | collected | refunded | rejected
    payment_method = db.Column(db.String(20), nullable=False)  # cod | qr

    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    delivery_fee = db.Column(db.Numeric(12, 2), default=Decimal("0.00"))
    discount_amount = db.Column(db.Numeric(12, 2), default=Decimal("0.00"))
    total = db.Column(db.Numeric(12, 2), nullable=False)

    delivery_instructions = db.Column(db.Text, nullable=True)
    promo_code = db.Column(db.String(50), nullable=True)

    prep_estimate_minutes = db.Column(db.Integer, nullable=True)
    delivery_estimate_minutes = db.Column(db.Integer, nullable=True)

    cancellation_reason = db.Column(db.Text, nullable=True)
    rejected_reason = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    preparing_at = db.Column(db.DateTime, nullable=True)
    ready_at = db.Column(db.DateTime, nullable=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    out_for_delivery_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    address = db.relationship("DeliveryAddress", back_populates="order", uselist=False, cascade="all, delete-orphan")
    assignment = db.relationship("DeliveryAssignment", back_populates="order", uselist=False, cascade="all, delete-orphan")

    @staticmethod
    def generate_order_number():
        return f"MH{datetime.utcnow().strftime('%y%m%d')}{secrets.token_hex(3).upper()}"

    @staticmethod
    def generate_tracking_token():
        return secrets.token_urlsafe(32)

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in VALID_TRANSITIONS.get(self.status, set())

    def to_dict(self, include_items=True, public=False):
        data = {
            "id": self.id,
            "order_number": self.order_number,
            "status": self.status,
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "subtotal": str(self.subtotal),
            "delivery_fee": str(self.delivery_fee),
            "discount_amount": str(self.discount_amount),
            "total": str(self.total),
            "is_guest": self.is_guest,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
        }
        if not public:
            data["tracking_token"] = self.tracking_token
            data["guest_name"] = self.guest_name
            data["guest_phone"] = self.guest_phone
            data["user_id"] = self.user_id
        if include_items:
            data["items"] = [i.to_dict() for i in self.items]
        if self.address:
            data["address"] = self.address.to_dict()
        if self.assignment:
            data["assignment"] = self.assignment.to_dict()
        return data


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False)
    food_id = db.Column(db.String(36), nullable=True)  # snapshot may outlive food
    food_name_en = db.Column(db.String(150), nullable=False)
    food_name_ne = db.Column(db.String(150), nullable=True)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")
    customizations = db.relationship("OrderItemCustomization", back_populates="order_item", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "food_name_en": self.food_name_en,
            "food_name_ne": self.food_name_ne,
            "unit_price": str(self.unit_price),
            "quantity": self.quantity,
            "line_total": str(self.line_total),
            "customizations": [c.to_dict() for c in self.customizations],
        }


class OrderItemCustomization(db.Model):
    __tablename__ = "order_item_customizations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_item_id = db.Column(db.String(36), db.ForeignKey("order_items.id"), nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    option_name = db.Column(db.String(100), nullable=False)
    price_delta = db.Column(db.Numeric(12, 2), default=Decimal("0.00"))
    quantity = db.Column(db.Integer, default=1)

    order_item = db.relationship("OrderItem", back_populates="customizations")

    def to_dict(self):
        return {
            "group_name": self.group_name,
            "option_name": self.option_name,
            "price_delta": str(self.price_delta),
            "quantity": self.quantity,
        }


class DeliveryAddress(db.Model):
    __tablename__ = "delivery_addresses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), unique=True, nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    landmark = db.Column(db.String(200), nullable=True)

    order = db.relationship("Order", back_populates="address")

    def to_dict(self):
        return {
            "full_address": self.full_address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "landmark": self.landmark,
        }


class DeliveryAssignment(db.Model):
    __tablename__ = "delivery_assignments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), unique=True, nullable=False)
    delivery_slot_id = db.Column(db.Integer, db.ForeignKey("delivery_identity_slots.id"), nullable=False)
    staff_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    order = db.relationship("Order", back_populates="assignment")
    location_updates = db.relationship("LocationUpdate", back_populates="assignment", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "delivery_slot_id": self.delivery_slot_id,
            "staff_user_id": self.staff_user_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
        }


class LocationUpdate(db.Model):
    __tablename__ = "location_updates"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = db.Column(db.String(36), db.ForeignKey("delivery_assignments.id"), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    accuracy_meters = db.Column(db.Float, nullable=True)

    assignment = db.relationship("DeliveryAssignment", back_populates="location_updates")
