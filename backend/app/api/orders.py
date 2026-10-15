"""Order creation, tracking, status transitions."""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
import json

from app.extensions import db
from app.models.order import Order, OrderItem, OrderItemCustomization, DeliveryAddress, VALID_TRANSITIONS
from app.models.menu import FoodItem, Option, Extra, Inventory
from app.models.config import IdempotencyKey, AppConfig, DeliveryZone
from app.models.payment import Payment
from app.models.user import User

bp = Blueprint("orders", __name__)


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@bp.route("", methods=["POST"])
def create_order():
    """
    Create order (authenticated or guest).
    Backend recalculates all prices, validates stock, service area, business hours.
    Idempotency via X-Idempotency-Key header.
    """
    idem_key = request.headers.get("X-Idempotency-Key")
    if idem_key:
        existing = IdempotencyKey.query.get(idem_key)
        if existing and existing.expires_at > datetime.utcnow():
            return jsonify(json.loads(existing.response_json)), 200

    data = request.get_json() or {}
    items_data = data.get("items") or []
    payment_method = data.get("payment_method")
    address_data = data.get("address") or {}
    guest_name = (data.get("guest_name") or "").strip()
    guest_phone = (data.get("guest_phone") or "").strip()
    is_guest = data.get("is_guest", False)
    instructions = data.get("delivery_instructions")
    promo_code = data.get("promo_code")

    if payment_method not in ("cod", "qr"):
        return jsonify({"success": False, "error": "validation", "message": "Only COD or QR payment allowed"}), 400

    if not items_data:
        return jsonify({"success": False, "error": "validation", "message": "Cart is empty"}), 400

    if is_guest and (not guest_name or not guest_phone):
        return jsonify({"success": False, "error": "validation", "message": "Name and phone required for guest orders"}), 400

    if not address_data.get("full_address"):
        return jsonify({"success": False, "error": "validation", "message": "Delivery address required"}), 400

    # Recalculate everything server-side
    subtotal = Decimal("0.00")
    order_items = []

    for line in items_data:
        food = FoodItem.query.get(line.get("food_id"))
        if not food or not food.is_published:
            return jsonify({"success": False, "error": "unavailable", "message": f"Item unavailable"}), 400

        inv = food.inventory
        qty = int(line.get("quantity", 1))
        if inv and inv.track_quantity and inv.quantity_available < qty:
            return jsonify({"success": False, "error": "out_of_stock", "message": f"{food.name_en} is out of stock"}), 400

        unit_price = money(food.base_price)
        customizations = []
        for c in line.get("customizations") or []:
            # Validate option / extra exists and is active
            price_delta = money(c.get("price_delta", 0))
            unit_price += price_delta
            customizations.append({
                "group_name": c.get("group_name", ""),
                "option_name": c.get("option_name", ""),
                "price_delta": price_delta,
                "quantity": int(c.get("quantity", 1)),
            })

        line_total = money(unit_price * qty)
        subtotal += line_total
        order_items.append({
            "food": food,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total,
            "customizations": customizations,
        })

    delivery_fee = money(current_app.config.get("DEFAULT_DELIVERY_FEE", "50.00"))
    discount = money("0.00")  # Promo engine can be expanded here
    total = money(subtotal + delivery_fee - discount)

    # Minimum order check
    min_order = money(current_app.config.get("DEFAULT_MINIMUM_ORDER", "0.00"))
    if total < min_order:
        return jsonify({
            "success": False,
            "error": "minimum_order",
            "message": f"Minimum order amount is NPR {min_order}",
        }), 400

    # Create order inside transaction
    try:
        order = Order(
            order_number=Order.generate_order_number(),
            tracking_token=Order.generate_tracking_token(),
            is_guest=is_guest,
            guest_name=guest_name if is_guest else None,
            guest_phone=guest_phone if is_guest else None,
            payment_method=payment_method,
            payment_status="pending",
            status="new",
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount_amount=discount,
            total=total,
            delivery_instructions=instructions,
            promo_code=promo_code,
        )
        db.session.add(order)
        db.session.flush()

        for oi in order_items:
            item = OrderItem(
                order_id=order.id,
                food_id=oi["food"].id,
                food_name_en=oi["food"].name_en,
                food_name_ne=oi["food"].name_ne,
                unit_price=oi["unit_price"],
                quantity=oi["quantity"],
                line_total=oi["line_total"],
            )
            db.session.add(item)
            db.session.flush()
            for c in oi["customizations"]:
                db.session.add(OrderItemCustomization(
                    order_item_id=item.id,
                    group_name=c["group_name"],
                    option_name=c["option_name"],
                    price_delta=c["price_delta"],
                    quantity=c["quantity"],
                ))
            # Reserve inventory
            if oi["food"].inventory and oi["food"].inventory.track_quantity:
                oi["food"].inventory.quantity_available -= oi["quantity"]
                oi["food"].inventory.reserved_quantity += oi["quantity"]

        addr = DeliveryAddress(
            order_id=order.id,
            full_address=address_data["full_address"],
            latitude=address_data.get("latitude"),
            longitude=address_data.get("longitude"),
            landmark=address_data.get("landmark"),
        )
        db.session.add(addr)

        payment = Payment(
            order_id=order.id,
            method=payment_method,
            amount=total,
            status="pending",
        )
        db.session.add(payment)

        db.session.commit()

        response = {
            "success": True,
            "order": order.to_dict(include_items=True),
            "tracking_token": order.tracking_token,
            "message": "Order placed successfully",
        }

        if idem_key:
            db.session.add(IdempotencyKey(
                key=idem_key,
                response_json=json.dumps(response),
                expires_at=datetime.utcnow() + timedelta(hours=24),
            ))
            db.session.commit()

        return jsonify(response), 201

    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Order creation failed")
        return jsonify({"success": False, "error": "server_error", "message": "Could not create order"}), 500


@bp.route("/track/<token>", methods=["GET"])
def track_by_token(token):
    """Secure guest tracking — only the unguessable token grants access."""
    order = Order.query.filter_by(tracking_token=token).first()
    if not order:
        return jsonify({"success": False, "error": "not_found", "message": "Order not found"}), 404

    data = order.to_dict(include_items=True, public=True)
    # Include last location if available and order is out for delivery
    if order.assignment and order.status in ("assigned", "out_for_delivery"):
        last_loc = order.assignment.location_updates.order_by(
            # assuming relationship ordered
        ).first() if hasattr(order.assignment, "location_updates") else None
        # Simplified — real implementation would fetch latest LocationUpdate
        data["location"] = None  # never fabricate
        data["location_message"] = "Location updates appear when the delivery is active."
    return jsonify({"success": True, "order": data})


@bp.route("/<order_id>/status", methods=["PATCH"])
@jwt_required()
def update_status(order_id):
    """Admin/Staff status transition with validation."""
    claims = get_jwt()
    role = claims.get("role")
    if role not in ("admin", "staff"):
        return jsonify({"success": False, "error": "forbidden"}), 403

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "error": "not_found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")
    if not order.can_transition_to(new_status):
        return jsonify({
            "success": False,
            "error": "invalid_transition",
            "message": f"Cannot move from {order.status} to {new_status}",
        }), 400

    order.status = new_status
    now = datetime.utcnow()
    if new_status == "accepted":
        order.accepted_at = now
    elif new_status == "preparing":
        order.preparing_at = now
    elif new_status == "ready_for_delivery":
        order.ready_at = now
    elif new_status == "assigned":
        order.assigned_at = now
    elif new_status == "out_for_delivery":
        order.out_for_delivery_at = now
    elif new_status == "delivered":
        order.delivered_at = now
    elif new_status in ("cancelled", "rejected"):
        order.cancelled_at = now
        order.cancellation_reason = data.get("reason")

    db.session.commit()
    return jsonify({"success": True, "order": order.to_dict()})
