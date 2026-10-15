from datetime import datetime
from decimal import Decimal
from app.extensions import db
import uuid


class Promotion(db.Model):
    __tablename__ = "promotions"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage | fixed
    discount_value = db.Column(db.Numeric(12, 2), nullable=False)
    min_order_amount = db.Column(db.Numeric(12, 2), default=Decimal("0.00"))
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    usage_limit = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0)


class PromoCode(db.Model):
    __tablename__ = "promo_codes"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    promotion_id = db.Column(db.String(36), db.ForeignKey("promotions.id"), nullable=False)
    max_uses = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class Banner(db.Model):
    __tablename__ = "banners"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(150), nullable=True)
    subtitle = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    click_url = db.Column(db.String(500), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)


class Advertisement(db.Model):
    __tablename__ = "advertisements"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    placement = db.Column(db.String(50), default="home")
    click_url = db.Column(db.String(500), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_sponsored = db.Column(db.Boolean, default=True)
