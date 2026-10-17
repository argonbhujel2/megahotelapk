"""Admin-only endpoints. All require role=admin."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.delivery import DeliveryIdentitySlot
from app.models.order import Order
from app.models.user import User
from app.services.bootstrap import ensure_delivery_slots

bp = Blueprint("admin", __name__)


def require_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return False
    return True


@bp.route("/delivery-slots", methods=["GET"])
@jwt_required()
def get_delivery_slots():
    if not require_admin():
        return jsonify({"success": False, "error": "forbidden"}), 403
    ensure_delivery_slots()
    slots = DeliveryIdentitySlot.query.order_by(DeliveryIdentitySlot.id).all()
    return jsonify({"success": True, "slots": [s.to_dict() for s in slots]})


@bp.route("/delivery-slots/<int:slot_id>", methods=["PATCH"])
@jwt_required()
def update_delivery_slot(slot_id):
    """Admin may only edit the two existing slots. Cannot create a third."""
    if not require_admin():
        return jsonify({"success": False, "error": "forbidden"}), 403
    if slot_id not in (1, 2):
        return jsonify({"success": False, "error": "invalid_slot", "message": "Only slots 1 and 2 exist"}), 400

    slot = DeliveryIdentitySlot.query.get(slot_id)
    if not slot:
        return jsonify({"success": False, "error": "not_found"}), 404

    data = request.get_json() or {}
    if "display_name" in data:
        slot.display_name = (data["display_name"] or "").strip() or None
    if "is_active" in data:
        slot.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify({"success": True, "slot": slot.to_dict()})


@bp.route("/orders", methods=["GET"])
@jwt_required()
def list_orders():
    if not require_admin():
        return jsonify({"success": False, "error": "forbidden"}), 403
    status = request.args.get("status")
    query = Order.query.order_by(Order.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    orders = query.limit(100).all()
    return jsonify({"success": True, "orders": [o.to_dict() for o in orders]})


@bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not require_admin():
        return jsonify({"success": False, "error": "forbidden"}), 403
    counts = {
        "new": Order.query.filter_by(status="new").count(),
        "preparing": Order.query.filter_by(status="preparing").count(),
        "out_for_delivery": Order.query.filter_by(status="out_for_delivery").count(),
        "pending_qr": Order.query.filter_by(payment_method="qr", payment_status="pending").count(),
    }
    return jsonify({"success": True, "counts": counts})
