"""Staff endpoints — restricted by StaffPermission."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models.user import User, StaffPermission
from app.models.order import Order, DeliveryAssignment, LocationUpdate
from app.models.payment import CODCollection
from datetime import datetime

bp = Blueprint("staff", __name__)


@bp.route("/assigned-orders", methods=["GET"])
@jwt_required()
def assigned_orders():
    claims = get_jwt()
    if claims.get("role") not in ("staff", "admin"):
        return jsonify({"success": False, "error": "forbidden"}), 403
    user_id = get_jwt_identity()
    assignments = DeliveryAssignment.query.filter_by(staff_user_id=user_id).all()
    orders = [a.order.to_dict() for a in assignments if a.order]
    return jsonify({"success": True, "orders": orders})


@bp.route("/location", methods=["POST"])
@jwt_required()
def update_location():
    """Staff posts actual device location during active delivery. Never fabricate."""
    claims = get_jwt()
    if claims.get("role") not in ("staff", "admin"):
        return jsonify({"success": False, "error": "forbidden"}), 403

    data = request.get_json() or {}
    assignment_id = data.get("assignment_id")
    lat = data.get("latitude")
    lng = data.get("longitude")
    if not assignment_id or lat is None or lng is None:
        return jsonify({"success": False, "error": "validation"}), 400

    assignment = DeliveryAssignment.query.get(assignment_id)
    if not assignment or assignment.staff_user_id != get_jwt_identity():
        return jsonify({"success": False, "error": "forbidden"}), 403

    if assignment.order.status not in ("assigned", "out_for_delivery"):
        return jsonify({"success": False, "error": "invalid_state"}), 400

    loc = LocationUpdate(
        assignment_id=assignment.id,
        latitude=float(lat),
        longitude=float(lng),
        accuracy_meters=data.get("accuracy"),
    )
    db.session.add(loc)
    db.session.commit()
    return jsonify({"success": True})


@bp.route("/cod-collect/<order_id>", methods=["POST"])
@jwt_required()
def collect_cod(order_id):
    claims = get_jwt()
    if claims.get("role") not in ("staff", "admin"):
        return jsonify({"success": False, "error": "forbidden"}), 403

    user_id = get_jwt_identity()
    perm = StaffPermission.query.filter_by(user_id=user_id).first()
    if claims.get("role") == "staff" and (not perm or not perm.can_confirm_cod):
        return jsonify({"success": False, "error": "forbidden"}), 403

    order = Order.query.get(order_id)
    if not order or order.payment_method != "cod":
        return jsonify({"success": False, "error": "invalid"}), 400
    if order.payment_status == "collected":
        return jsonify({"success": False, "error": "already_collected"}), 400

    existing = CODCollection.query.filter_by(order_id=order_id).first()
    if existing:
        return jsonify({"success": False, "error": "already_collected"}), 400

    coll = CODCollection(
        order_id=order_id,
        collected_by=user_id,
        amount=order.total,
    )
    order.payment_status = "collected"
    db.session.add(coll)
    db.session.commit()
    return jsonify({"success": True, "message": "COD marked as collected"})
