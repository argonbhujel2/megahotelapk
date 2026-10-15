from datetime import datetime
from app.extensions import db
import uuid


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False)
    food_id = db.Column(db.String(36), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    is_visible = db.Column(db.Boolean, default=True)
    moderated_by = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("order_id", "food_id", "user_id", name="uq_review_per_order_item"),
    )
