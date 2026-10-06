import os

from flask import Flask, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from sqlalchemy import inspect, text

from config import Config
from extensions import db
from seed import seed_admin, seed_if_empty

# Import models
import models  # noqa: F401

from routes_admin import bp as admin_bp
from routes_auth import bp as auth_bp
from routes_bookings import bp as bookings_bp
from routes_profile import bp as profile_bp
from routes_providers import bp as providers_bp


_NEW_COLUMNS = {
    "users": [
        ("street", "VARCHAR"),
        ("pincode", "VARCHAR"),
        ("is_active", "BOOLEAN NOT NULL DEFAULT TRUE"),
    ],
    "providers": [
        ("active", "BOOLEAN NOT NULL DEFAULT TRUE"),
    ],
}


def migrate_schema():
    inspector = inspect(db.engine)

    for table, columns in _NEW_COLUMNS.items():
        existing = {c["name"] for c in inspector.get_columns(table)}

        for name, ddl in columns:
            if name not in existing:
                db.session.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
                )

    db.session.commit()


def create_app():

    # frontend folder is inside the project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path=""
    )

    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1
    )

    CORS(
        app,
        supports_credentials=True,
        origins=Config.CORS_ORIGINS
    )

    db.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(providers_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # =========================
    # HOME PAGE
    # =========================

    @app.route("/")
    def home():
        return send_from_directory(
            frontend_dir,
            "Radius.html"
        )

    # =========================
    # STATIC FILES
    # =========================

    @app.route("/<path:filename>")
    def static_files(filename):

        # Do not intercept API routes
        if filename.startswith("api/"):
            return
