import os

from flask import Flask, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from sqlalchemy import inspect, text

from config import Config
from extensions import db
from seed import seed_admin, seed_if_empty

import models  # noqa: F401

from routes_admin import bp as admin_bp
from routes_auth import bp as auth_bp
from routes_bookings import bp as bookings_bp
from routes_profile import bp as profile_bp
from routes_providers import bp as providers_bp


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# If frontend folder doesn't exist, use project root
if not os.path.isdir(FRONTEND_DIR):
    FRONTEND_DIR = BASE_DIR


# ============================================================
# FLASK APP
# IMPORTANT: Vercel requires a top-level "app"
# ============================================================

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

app.config.from_object(Config)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# ============================================================
# CORS
# ============================================================

CORS(
    app,
    supports_credentials=True,
    origins=Config.CORS_ORIGINS
)


# ============================================================
# DATABASE
# ============================================================

db.init_app(app)


# ============================================================
# BLUEPRINTS
# ============================================================

app.register_blueprint(auth_bp)
app.register_blueprint(providers_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)


# ============================================================
# DATABASE MIGRATION
# ============================================================

_NEW_COLUMNS = {
    "users": [
        ("street", "VARCHAR"),
        ("pincode", "VARCHAR"),
        ("is_active", "BOOLEAN NOT NULL DEFAULT TRUE")
    ],
    "providers": [
        ("active", "BOOLEAN NOT NULL DEFAULT TRUE")
    ]
}


def migrate_schema():

    inspector = inspect(db.engine)

    for table, columns in _NEW_COLUMNS.items():

        existing = {
            column["name"]
            for column in inspector.get_columns(table)
        }

        for name, ddl in columns:

            if name not in existing:

                db.session.execute(
                    text(
                        f"ALTER TABLE {table} "
                        f"ADD COLUMN {name} {ddl}"
                    )
                )

    db.session.commit()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    radius_file = os.path.join(
        FRONTEND_DIR,
        "Radius.html"
    )

    if os.path.isfile(radius_file):

        return send_from_directory(
            FRONTEND_DIR,
            "Radius.html"
        )

    return jsonify(
        error="Radius.html not found"
    ), 404


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():

    try:

        db.session.execute(
            text("SELECT 1")
        )

        return jsonify(
            status="ok",
            database="connected"
        )

    except Exception as e:

        db.session.rollback()

        return jsonify(
            status="error",
            database="not connected",
            error=str(e)
        ), 500


# ============================================================
# STATIC FILES
# ============================================================

@app.route("/<path:filename>")
def static_files(filename):

    # Don't intercept API routes
    if filename.startswith("api/"):
        return jsonify(
            error="Not found"
        ), 404

    file_path = os.path.join(
        FRONTEND_DIR,
        filename
    )

    if os.path.isfile(file_path):

        return send_from_directory(
            FRONTEND_DIR,
            filename
        )

    return jsonify(
        error="Not found"
    ), 404


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(_error):

    return jsonify(
        error="Not found"
    ), 404


@app.errorhandler(405)
def method_not_allowed(_error):

    return jsonify(
        error="Method not allowed"
    ), 405


@app.errorhandler(500)
def server_error(_error):

    try:
        db.session.rollback()
    except Exception:
        pass

    return jsonify(
        error="Internal server error"
    ), 500


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():

    try:

        db.create_all()

        migrate_schema()

        seed_if_empty()

        seed_admin()

        print(
            "Radius database initialized successfully."
        )

    except Exception as error:

        print(
            "Database initialization error:",
            error
        )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
