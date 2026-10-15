"""
Mega Hotel Delivery â€” Flask application factory.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from .extensions import db, migrate, jwt
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config.get("CORS_ORIGINS", ["*"]))

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get("RATELIMIT_DEFAULT", "200 per day")],
        storage_uri="memory://",
    )
    limiter.init_app(app)
    app.limiter = limiter

    # Blueprints
    from .api.auth import bp as auth_bp
    from .api.menu import bp as menu_bp
    from .api.orders import bp as orders_bp
    from .api.admin import bp as admin_bp
    from .api.staff import bp as staff_bp
    from .api.payments import bp as payments_bp
    from .api.support import bp as support_bp
    from .api.public import bp as public_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(menu_bp, url_prefix="/api/v1/menu")
    app.register_blueprint(orders_bp, url_prefix="/api/v1/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(staff_bp, url_prefix="/api/v1/staff")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments")
    app.register_blueprint(support_bp, url_prefix="/api/v1/support")
    app.register_blueprint(public_bp, url_prefix="/api/v1")

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "bad_request", "message": str(e.description)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": "unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "forbidden", "message": "Insufficient permissions"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def ratelimit(e):
        return jsonify({"success": False, "error": "rate_limit", "message": "Too many requests"}), 429

    @app.errorhandler(500)
    def internal(e):
        return jsonify({"success": False, "error": "internal_error", "message": "An unexpected error occurred"}), 500

    # Health check
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "mega-hotel-delivery"}), 200

    # Bootstrap admin if enabled
    with app.app_context():
        from .services.bootstrap import ensure_admin_bootstrap
        ensure_admin_bootstrap()

    return app

