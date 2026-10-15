from datetime import datetime
from app.extensions import db
import uuid


class AppConfig(db.Model):
    __tablename__ = "app_config"
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BusinessHours(db.Model):
    __tablename__ = "business_hours"
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday ... 6=Sunday
    open_time = db.Column(db.String(5), nullable=True)  # HH:MM
    close_time = db.Column(db.String(5), nullable=True)
    is_closed = db.Column(db.Boolean, default=False)


class DeliveryZone(db.Model):
    __tablename__ = "delivery_zones"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    # Simple polygon or radius can be added later; for now name + active flag
    center_lat = db.Column(db.Float, nullable=True)
    center_lng = db.Column(db.Float, nullable=True)
    radius_km = db.Column(db.Float, nullable=True)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = db.Column(db.String(36), nullable=True)
    actor_role = db.Column(db.String(20), nullable=True)
    action = db.Column(db.String(80), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(36), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class IdempotencyKey(db.Model):
    __tablename__ = "idempotency_keys"
    key = db.Column(db.String(64), primary_key=True)
    response_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
