"""Menu, categories, options, extras and inventory."""
from datetime import datetime
from decimal import Decimal
from app.extensions import db
import uuid


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = db.Column(db.String(80), unique=True, nullable=False)
    name_en = db.Column(db.String(120), nullable=False)
    name_ne = db.Column(db.String(120), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    foods = db.relationship("FoodItem", back_populates="category")

    def to_dict(self, lang="en"):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name_ne if lang == "ne" and self.name_ne else self.name_en,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "image_url": self.image_url,
        }


class FoodItem(db.Model):
    __tablename__ = "food_items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id"), nullable=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    name_en = db.Column(db.String(150), nullable=False)
    name_ne = db.Column(db.String(150), nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    description_ne = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500), nullable=True)
    fallback_image_key = db.Column(db.String(80), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("Category", back_populates="foods")
    option_groups = db.relationship("OptionGroup", back_populates="food", cascade="all, delete-orphan")
    inventory = db.relationship("Inventory", back_populates="food", uselist=False, cascade="all, delete-orphan")

    def to_dict(self, lang="en", include_options=False):
        data = {
            "id": self.id,
            "category_id": self.category_id,
            "slug": self.slug,
            "name": self.name_ne if lang == "ne" and self.name_ne else self.name_en,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "description": self.description_ne if lang == "ne" and self.description_ne else self.description_en,
            "base_price": str(self.base_price),
            "is_vegetarian": self.is_vegetarian,
            "is_published": self.is_published,
            "is_featured": self.is_featured,
            "image_url": self.image_url,
            "fallback_image_key": self.fallback_image_key,
            "available": self._is_available(),
        }
        if include_options:
            data["option_groups"] = [g.to_dict(lang) for g in self.option_groups if g.is_active]
        return data

    def _is_available(self):
        if not self.is_published:
            return False
        if self.inventory:
            if self.inventory.track_quantity and self.inventory.quantity_available <= 0:
                return False
            if not self.inventory.is_available:
                return False
        return True


class OptionGroup(db.Model):
    """Size / variant / extra group. Can be required or optional."""
    __tablename__ = "option_groups"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    food_id = db.Column(db.String(36), db.ForeignKey("food_items.id"), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    name_ne = db.Column(db.String(100), nullable=True)
    is_required = db.Column(db.Boolean, default=False)
    min_select = db.Column(db.Integer, default=0)
    max_select = db.Column(db.Integer, default=1)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    food = db.relationship("FoodItem", back_populates="option_groups")
    options = db.relationship("Option", back_populates="group", cascade="all, delete-orphan")

    def to_dict(self, lang="en"):
        return {
            "id": self.id,
            "name": self.name_ne if lang == "ne" and self.name_ne else self.name_en,
            "is_required": self.is_required,
            "min_select": self.min_select,
            "max_select": self.max_select,
            "options": [o.to_dict(lang) for o in self.options if o.is_active],
        }


class Option(db.Model):
    __tablename__ = "options"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = db.Column(db.String(36), db.ForeignKey("option_groups.id"), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    name_ne = db.Column(db.String(100), nullable=True)
    price_delta = db.Column(db.Numeric(12, 2), default=Decimal("0.00"))
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    group = db.relationship("OptionGroup", back_populates="options")

    def to_dict(self, lang="en"):
        return {
            "id": self.id,
            "name": self.name_ne if lang == "ne" and self.name_ne else self.name_en,
            "price_delta": str(self.price_delta),
            "is_default": self.is_default,
        }


class Extra(db.Model):
    """Standalone extras / add-ons that can have quantity limits."""
    __tablename__ = "extras"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    food_id = db.Column(db.String(36), db.ForeignKey("food_items.id"), nullable=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ne = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    max_quantity = db.Column(db.Integer, default=5)
    is_active = db.Column(db.Boolean, default=True)
    track_inventory = db.Column(db.Boolean, default=False)
    quantity_available = db.Column(db.Integer, default=0)

    def to_dict(self, lang="en"):
        return {
            "id": self.id,
            "name": self.name_ne if lang == "ne" and self.name_ne else self.name_en,
            "price": str(self.price),
            "max_quantity": self.max_quantity,
            "available": not self.track_inventory or self.quantity_available > 0,
        }


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    food_id = db.Column(db.String(36), db.ForeignKey("food_items.id"), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    track_quantity = db.Column(db.Boolean, default=False)
    quantity_available = db.Column(db.Integer, default=0)
    reserved_quantity = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    food = db.relationship("FoodItem", back_populates="inventory")
