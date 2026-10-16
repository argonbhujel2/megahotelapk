"""Authentication endpoints â€” shared login for all roles."""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import uuid

from app.extensions import db
from app.models.user import User, Session
from app.models.delivery import DeliveryIdentitySlot

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    """
    Shared login. Backend determines role after successful authentication.
    Never trust a client-supplied role.
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "error": "validation", "message": "Email and password required"}), 400

    user = User.query.filter_by(email=email, is_active=True).first()

    password_valid = False
    if user and user.password_hash:
        try:
            password_valid = check_password_hash(user.password_hash, password)
        except (ValueError, TypeError):
            current_app.logger.warning(
                "Login rejected because the stored password hash is invalid."
            )

    if not password_valid:
        return jsonify({
            "success": False,
            "error": "invalid_credentials",
            "message": "Invalid email or password",
        }), 401

    user.last_login_at = datetime.utcnow()
    access = create_access_token(identity=user.id, additional_claims={"role": user.role})
    refresh = create_refresh_token(identity=user.id)

    # Store refresh session for revocation
    session = Session(
        user_id=user.id,
        refresh_token_jti=str(uuid.uuid4()),
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.remote_addr,
        expires_at=datetime.utcnow() + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "success": True,
        "access_token": access,
        "refresh_token": refresh,
        "user": user.to_dict(),
    })


@bp.route("/guest", methods=["POST"])
def guest_entry():
    """Continue as Guest â€” no account created."""
    return jsonify({
        "success": True,
        "guest": True,
        "message": "Guest session started. You can browse and place orders.",
    })


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or not user.is_active:
        return jsonify({"success": False, "error": "invalid_user"}), 401
    access = create_access_token(identity=user.id, additional_claims={"role": user.role})
    return jsonify({"success": True, "access_token": access})


@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # In a full implementation, mark the refresh JTI as revoked
    return jsonify({"success": True, "message": "Logged out"})


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"success": False, "error": "not_found"}), 404
    return jsonify({"success": True, "user": user.to_dict()})


@bp.route("/password-reset-request", methods=["POST"])
def password_reset_request():
    """Generic response to avoid account enumeration."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    # In production: generate single-use token, email it, expire after short window
    return jsonify({
        "success": True,
        "message": "If an account exists for that email, a reset link has been sent.",
    })

