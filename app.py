import os

from flask import Flask, jsonify, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from sqlalchemy import inspect, text

from config import Config
from extensions import db
from seed import seed_admin, seed_if_empty

# Import models so SQLAlchemy registers them before db.create_all() runs.
import models  # noqa: F401

from routes_admin import bp as admin_bp
from routes_auth import bp as auth_bp
from routes_bookings import bp as bookings_bp
from routes_profile import bp as profile_bp
from routes_providers import bp as providers_bp


# Columns added after the first release. db.create_all() never alters an
# existing table, so older radius.db files are upgraded in place here.
_NEW_COLUMNS = {
    "users": [("street", "VARCHAR"), ("pincode", "VARCHAR"), ("is_active", "BOOLEAN NOT NULL DEFAULT TRUE")],
    "providers": [("active", "BOOLEAN NOT NULL DEFAULT TRUE")],
}


def migrate_schema():
    inspector = inspect(db.engine)
    for table, columns in _NEW_COLUMNS.items():
        existing = {c["name"] for c in inspector.get_columns(table)}
        for name, ddl in columns:
            if name not in existing:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
    db.session.commit()


def create_app():
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
    # The same service serves the website (frontend/) and the API (/api/...),
    # so in production there is a single origin and no CORS/cookie trouble.
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    @app.route("/")
    def home():
        return redirect("/Radius.html")

    # supports_credentials is required so the session cookie (login state)
    # is sent/received on cross-origin requests from the frontend.
    CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(providers_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    @app.route("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def bad_method(_e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def server_error(_e):
        db.session.rollback()
        return jsonify(error="Internal server error"), 500

    with app.app_context():
        db.create_all()
        migrate_schema()
        seed_if_empty()
        seed_admin()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
