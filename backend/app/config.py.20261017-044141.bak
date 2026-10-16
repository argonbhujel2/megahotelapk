import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 2592000)))

    # Database
    # Prefer Turso when credentials present; otherwise local SQLite for development
    TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
    TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {},
    }

    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN and "libsql" in (DATABASE_URL or ""):
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
            "auth_token": TURSO_AUTH_TOKEN,
        }

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

