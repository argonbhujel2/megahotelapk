from datetime import datetime
from app.extensions import db
import uuid


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=True)
    guest_email_or_phone = db.Column(db.String(150), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default="open")  # open | in_progress | resolved | closed
    assigned_to = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")


class TicketMessage(db.Model):
    __tablename__ = "ticket_messages"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(36), db.ForeignKey("support_tickets.id"), nullable=False)
    sender_id = db.Column(db.String(36), nullable=True)
    sender_role = db.Column(db.String(20), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("SupportTicket", back_populates="messages")
