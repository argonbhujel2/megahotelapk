"""Public configuration and health-related endpoints."""
from flask import Blueprint, jsonify, current_app
from app.models.promo import Banner
from datetime import datetime

bp = Blueprint("public", __name__)


@bp.route("/config", methods=["GET"])
def app_config():
    return jsonify({
        "success": True,
        "minimum_app_version": current_app.config.get("MINIMUM_APP_VERSION", "1.0.0"),
        "delivery_fee": current_app.config.get("DEFAULT_DELIVERY_FEE", "50.00"),
        "currency": "NPR",
        "timezone": current_app.config.get("TIMEZONE", "Asia/Kathmandu"),
        "developer_credit_url": "https://bamstudio.argan.com.np/",
    })


@bp.route("/banners", methods=["GET"])
def active_banners():
    now = datetime.utcnow()
    banners = Banner.query.filter_by(is_active=True).order_by(Banner.sort_order).all()
    active = []
    for b in banners:
        if b.starts_at and b.starts_at > now:
            continue
        if b.ends_at and b.ends_at < now:
            continue
        active.append({
            "id": b.id,
            "title": b.title,
            "subtitle": b.subtitle,
            "image_url": b.image_url,
            "click_url": b.click_url,
        })
    return jsonify({"success": True, "banners": active})
