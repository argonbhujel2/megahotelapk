"""QR payment submission and verification."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.extensions import db
from app.models.order import Order
from app.models.payment import QRSubmission, Payment
from datetime import datetime

bp = Blueprint("payments", __name__)


@bp.route("/qr/submit", methods=["POST"])
def submit_qr():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    tracking_token = data.get("tracking_token")
    ref = (data.get("transaction_reference") or "").strip()
    screenshot = data.get("screenshot_url")

    if not ref:
        return jsonify({"success": False, "error": "validation", "message": "Transaction reference required"}), 400

    order = None
    if order_id:
        order = Order.query.get(order_id)
    elif tracking_token:
        order = Order.query.filter_by(tracking_token=tracking_token).first()

    if not order or order.payment_method != "qr":
        return jsonify({"success": False, "error": "not_found"}), 404

    existing = QRSubmission.query.filter_by(transaction_reference=ref).first()
    if existing:
        return jsonify({"success": False, "error": "duplicate_reference"}), 400

    sub = QRSubmission(
        order_id=order.id,
        transaction_reference=ref,
        screenshot_url=screenshot,
        status="pending",
    )
    order.payment_status = "submitted"
    db.session.add(sub)
    db.session.commit()
    return jsonify({"success": True, "message": "QR payment submitted for verification"})


@bp.route("/qr/<submission_id>/verify", methods=["POST"])
@jwt_required()
def verify_qr(submission_id):
    claims = get_jwt()
    role = claims.get("role")
    if role not in ("admin", "staff"):
        return jsonify({"success": False, "error": "forbidden"}), 403

    # Staff need explicit can_verify_qr permission (checked in full implementation)
    data = request.get_json() or {}
    decision = data.get("decision")  # approved | rejected
    reason = data.get("reason")

    sub = QRSubmission.query.get(submission_id)
    if not sub:
        return jsonify({"success": False, "error": "not_found"}), 404
    if sub.status != "pending":
        return jsonify({"success": False, "error": "already_decided"}), 400

    sub.status = decision
    sub.verified_by = get_jwt_identity()
    sub.verified_at = datetime.utcnow()
    if decision == "rejected":
        sub.rejection_reason = reason
        sub.order.payment_status = "rejected"
    else:
        sub.order.payment_status = "verified"

    db.session.commit()
    return jsonify({"success": True, "status": decision})
