import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Central app configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-change-me"
    )

    # =========================================================
    # DATABASE
    # =========================================================

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        _db_url = DATABASE_URL

        # PostgreSQL URL compatibility
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = _db_url

    else:
        # Vercel project folder is read-only.
        # /tmp is writable on Vercel.
        SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/radius.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================================================
    # SESSION
    # =========================================================

    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True

    # Vercel uses HTTPS
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "1") == "1"
    )

    # =========================================================
    # CORS
    # =========================================================

    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5500,"
        "http://127.0.0.1:5500,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:8080,"
        "http://127.0.0.1:8080,"
        "https://radius12-1itw.vercel.app"
    ).split(",")

    # =========================================================
    # ADMIN
    # =========================================================

    ADMIN_EMAIL = os.environ.get(
        "ADMIN_EMAIL",
        "admin@radius.local"
    )

    ADMIN_PASSWORD = os.environ.get(
        "ADMIN_PASSWORD",
        "admin123"
    )
