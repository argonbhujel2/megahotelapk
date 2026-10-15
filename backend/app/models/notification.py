from datetime import datetime
from app.extensions import db
import uuid


class DeviceToken(db.Model):
    __tablename__ = "device_tokens"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(20), default="android")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    order_id = db.Column(db.String(36), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), default="transactional")  # transactional | promotional
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
