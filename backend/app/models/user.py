"""User, authentication and staff permission models."""
from datetime import datetime
from app.extensions import db
import uuid


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="customer")  # customer | admin | staff
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    language = db.Column(db.String(10), default="en")
    preferred_notifications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    identities = db.relationship("AuthIdentity", back_populates="user", cascade="all, delete-orphan")
    sessions = db.relationship("Session", back_populates="user", cascade="all, delete-orphan")
    staff_permissions = db.relationship("StaffPermission", back_populates="user", uselist=False)

    def to_dict(self, include_sensitive=False):
        data = {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_sensitive:
            data["last_login_at"] = self.last_login_at.isoformat() if self.last_login_at else None
        return data


class AuthIdentity(db.Model):
    """External OAuth identities (Google, Facebook)."""
    __tablename__ = "auth_identities"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    provider = db.Column(db.String(30), nullable=False)  # google | facebook | email
    provider_user_id = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="identities")

    __table_args__ = (
        db.UniqueConstraint("provider", "provider_user_id", name="uq_provider_identity"),
    )


class Session(db.Model):
    """Refresh-token / session tracking for revocation."""
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    refresh_token_jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_agent = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="sessions")


class StaffPermission(db.Model):
    """Granular permissions for Staff role."""
    __tablename__ = "staff_permissions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    can_update_order_status = db.Column(db.Boolean, default=True)
    can_confirm_cod = db.Column(db.Boolean, default=True)
    can_verify_qr = db.Column(db.Boolean, default=False)
    can_reply_support = db.Column(db.Boolean, default=False)
    can_view_reports = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="staff_permissions")
