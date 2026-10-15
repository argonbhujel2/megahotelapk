"""Payment, QR verification, COD collection and refunds."""
from datetime import datetime
from decimal import Decimal
from app.extensions import db
import uuid


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), unique=True, nullable=False)
    method = db.Column(db.String(20), nullable=False)  # cod | qr
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(30), default="pending")  # pending | submitted | verified | collected | rejected | refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QRSubmission(db.Model):
    __tablename__ = "qr_submissions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False)
    transaction_reference = db.Column(db.String(120), nullable=False, index=True)
    screenshot_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending | approved | rejected
    verified_by = db.Column(db.String(36), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("transaction_reference", name="uq_qr_transaction_ref"),
    )


class CODCollection(db.Model):
    __tablename__ = "cod_collections"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), unique=True, nullable=False)
    collected_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)


class Refund(db.Model):
    __tablename__ = "refunds"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    external_reference = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default="recorded")  # recorded | confirmed_external
    verified_by = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
