import os
from datetime import timedelta
from sqlalchemy.engine import URL


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 2592000)))

    # Database: prefer configured Turso credentials; otherwise use DATABASE_URL.
    TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
    TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")

    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        _turso_host = TURSO_DATABASE_URL.strip().rstrip("/")
        if _turso_host.startswith("libsql://"):
            _turso_host = _turso_host[len("libsql://"):]
        elif _turso_host.startswith("https://"):
            _turso_host = _turso_host[len("https://"):]
        elif _turso_host.startswith("http://"):
            _turso_host = _turso_host[len("http://"):]

        SQLALCHEMY_DATABASE_URI = URL.create(
            "sqlite+libsql_native",
            host=_turso_host,
            query={"secure": "true"},
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "connect_args": {"auth_token": TURSO_AUTH_TOKEN},
        }
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///local.db"
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "connect_args": {},
        }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Admin bootstrap
    ADMIN_BOOTSTRAP_ENABLED = os.getenv("ADMIN_BOOTSTRAP_ENABLED", "false").lower() == "true"
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@megahotel.local")
    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
    ADMIN_PASSWORD_RESET_ENABLED = (
        os.getenv("ADMIN_PASSWORD_RESET_ENABLED", "false").lower() == "true"
    )

    # Business defaults
    DEFAULT_DELIVERY_FEE = os.getenv("DEFAULT_DELIVERY_FEE", "50.00")
    DEFAULT_MINIMUM_ORDER = os.getenv("DEFAULT_MINIMUM_ORDER", "0.00")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kathmandu")
    MINIMUM_APP_VERSION = os.getenv("MINIMUM_APP_VERSION", "1.0.0")

    # Rate limits
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")

    # CORS
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "mega_hotel")

