"""Support tickets."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.support import SupportTicket, TicketMessage
import secrets
from datetime import datetime

bp = Blueprint("support", __name__)


@bp.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json() or {}
    subject = (data.get("subject") or "").strip()
    body = (data.get("body") or "").strip()
    if not subject or not body:
        return jsonify({"success": False, "error": "validation"}), 400

    ticket = SupportTicket(
        ticket_number=f"TK{secrets.token_hex(4).upper()}",
        subject=subject,
        guest_email_or_phone=data.get("contact"),
        order_id=data.get("order_id"),
        status="open",
    )
    db.session.add(ticket)
    db.session.flush()
    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_role="customer",
        body=body,
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"success": True, "ticket_number": ticket.ticket_number}), 201
