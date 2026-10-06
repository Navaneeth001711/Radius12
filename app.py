import os

from flask import Flask, jsonify, redirect
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

        if table not in inspector.get_table_names():
            continue

        existing = {
            column["name"]
            for column in inspector.get_columns(table)
        }

        for name, ddl in columns:
            if name not in existing:
                try:
                    db.session.execute(
                        text(
                            f"ALTER TABLE {table} "
                            f"ADD COLUMN {name} {ddl}"
                        )
                    )
                except Exception as e:
                    print(
                        f"Migration warning for {table}.{name}: {e}"
                    )
                    db.session.rollback()

        db.session.commit()


def configure_database(app):

    database_url = os.environ.get("DATABASE_URL")

    # ---------------------------------------------------------
    # Production: PostgreSQL
    # ---------------------------------------------------------
    if database_url:

        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1,
            )

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url

        print("Using PostgreSQL database")

    # ---------------------------------------------------------
    # Vercel fallback: temporary SQLite
    # ---------------------------------------------------------
    elif os.environ.get("VERCEL"):

        database_path = "/tmp/radius.db"

        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + database_path
        )

        print("WARNING: Using temporary Vercel SQLite database")

    # ---------------------------------------------------------
    # Local development
    # ---------------------------------------------------------
    else:

        database_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "radius.db",
        )

        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + database_path
        )

        print("Using local SQLite database")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def create_app():

    frontend_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "frontend",
    )

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path="",
    )

    app.config.from_object(Config)

    # Configure database AFTER loading Config
    configure_database(app)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
    )

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    CORS(
        app,
        supports_credentials=True,
        origins=Config.CORS_ORIGINS,
    )

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    db.init_app(app)

    # ---------------------------------------------------------
    # Blueprints
    # ---------------------------------------------------------

    app.register_blueprint(auth_bp)
    app.register_blueprint(providers_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # ---------------------------------------------------------
    # Home
    # ---------------------------------------------------------

    @app.route("/")
    def home():
        return redirect("/Radius.html")

    # ---------------------------------------------------------
    # Health check
    # ---------------------------------------------------------

    @app.route("/api/health")
    def health():

        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return jsonify(
                status="ok",
                database="connected"
            )

        except Exception as e:

            print("Database health error:", e)

            return jsonify(
                status="error",
                database="not connected"
            ), 500

    # ---------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def bad_method(_e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def server_error(_e):

        try:
            db.session.rollback()
        except Exception:
            pass

        return jsonify(
            error="Internal server error"
        ), 500

    # ---------------------------------------------------------
    # Database initialization
    # ---------------------------------------------------------

    with app.app_context():

        try:

            db.create_all()

            migrate_schema()

            seed_if_empty()

            seed_admin()

            print("Database initialization completed")

        except Exception as e:

            print(
                "Database initialization error:",
                e
            )

            try:
                db.session.rollback()
            except Exception:
                pass

    return app


# -------------------------------------------------------------
# WSGI application
# -------------------------------------------------------------

app = create_app()


# -------------------------------------------------------------
# Local development
# -------------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
