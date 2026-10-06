import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Central app configuration. Override any of these with environment
    variables in production (see .env.example)."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    _db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'radius.db')}")
    if _db_url.startswith("postgres://"):  # Render/Heroku style URL
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie holds the logged-in user's id (mirrors the
    # frontend's DB.currentUserId concept from Radius.html).
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    # Set SESSION_COOKIE_SECURE=1 in production (HTTPS only).
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

    # Origins allowed to call this API with credentials (cookies).
    # Add your deployed frontend's origin here, or set CORS_ORIGINS env var
    # as a comma-separated list. Serve the frontend over http(s), not
    # file://, so the session cookie can be set.
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:8080,http://127.0.0.1:8080",
    ).split(",")

    # Default admin account, created on first startup if no admin exists.
    # CHANGE THESE (env vars or .env) before any real deployment.
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@radius.local")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
