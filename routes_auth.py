from datetime import date

from flask import Blueprint, jsonify, request, session

from extensions import db
from models import Provider, Service, User
from seed import AP_CITIES, CATEGORIES, CITY_COORDS, jitter
from utils import clean, get_current_user, next_numeric_id, valid_email, valid_phone

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

MIN_PASSWORD = 6
CATEGORY_IDS = {c["id"] for c in CATEGORIES}


def _body():
    return request.get_json(silent=True) or {}


def _check_required(data, fields):
    for field in fields:
        if not str(data.get(field, "")).strip():
            return f"{field} is required"
    if len(str(data.get("password", ""))) < MIN_PASSWORD:
        return f"Password must be at least {MIN_PASSWORD} characters"
    if not valid_email(data.get("email")):
        return "Please enter a valid email address"
    if not valid_phone(data.get("phone")):
        return "Please enter a valid phone number"
    if data.get("city") not in AP_CITIES:
        return "Please select a valid city"
    return None


@bp.route("/register", methods=["POST"])
def register():
    """Customer sign-up."""
    data = _body()
    error = _check_required(data, ("name", "email", "phone", "city", "mandal", "password"))
    if error:
        return jsonify(error=error), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify(error="An account with that email already exists"), 409

    user = User(
        id=f"u{next_numeric_id(User, 'u', id_col=User.id)}",
        role="customer",
        name=clean(data["name"], 100),
        email=email,
        phone=clean(data["phone"], 20),
        city=data["city"],
        mandal=clean(data["mandal"], 100),
        joined_at=date.today().isoformat(),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify(user=user.to_dict()), 201


@bp.route("/register/worker", methods=["POST"])
def register_worker():
    """Worker sign-up: creates the user AND their public provider listing."""
    data = _body()
    error = _check_required(
        data, ("name", "email", "phone", "city", "mandal", "street", "pincode", "bio", "password")
    )
    if error:
        return jsonify(error=error), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify(error="An account with that email already exists"), 409

    categories = data.get("categories") or []
    if not isinstance(categories, list) or not categories:
        return jsonify(error="Please select at least one service category"), 400
    categories = [c for c in categories if c in CATEGORY_IDS]
    if not categories:
        return jsonify(error="Invalid service category"), 400

    services = []
    for s in data.get("services") or []:
        name = clean(s.get("name"), 100)
        try:
            price = int(s.get("price"))
        except (TypeError, ValueError):
            continue
        if name and price >= 0:
            services.append({"name": name, "price": price})
    if not services:
        return jsonify(error="Please add at least one service with a price"), 400

    user = User(
        id=f"u{next_numeric_id(User, 'u', id_col=User.id)}",
        role="worker",
        name=clean(data["name"], 100),
        email=email,
        phone=clean(data["phone"], 20),
        city=data["city"],
        mandal=clean(data["mandal"], 100),
        street=clean(data["street"], 200),
        pincode=clean(data["pincode"], 10),
        joined_at=date.today().isoformat(),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()

    provider_id = f"p{next_numeric_id(Provider, 'p', start=100, id_col=Provider.id)}_{user.id}"
    center = CITY_COORDS.get(data["city"], (16.5, 80.6))
    provider = Provider(
        id=provider_id,
        owner_id=user.id,
        name=user.name,
        phone=user.phone,
        category=categories[0],
        categories=",".join(categories),
        area=data["city"],
        street=user.street,
        mandal=user.mandal,
        pincode=user.pincode,
        lat=jitter(center[0], provider_id + "lat"),
        lng=jitter(center[1], provider_id + "lng"),
        bio=clean(data["bio"], 1000),
        review_count=0,
    )
    db.session.add(provider)
    db.session.flush()

    for s in services:
        db.session.add(Service(provider_id=provider.id, name=s["name"], price=s["price"]))

    db.session.commit()
    session["user_id"] = user.id
    return jsonify(user=user.to_dict(), provider=provider.to_dict(include_details=True)), 201


@bp.route("/login", methods=["POST"])
def login():
    data = _body()
    email = str(data.get("email", "")).strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(str(data.get("password", ""))):
        return jsonify(error="Invalid email or password"), 401
    if user.is_active is False:
        return jsonify(error="This account has been suspended. Please contact support."), 403

    session["user_id"] = user.id
    return jsonify(user=user.to_dict())


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify(ok=True)


@bp.route("/me")
def me():
    user = get_current_user()
    return jsonify(user=user.to_dict() if user else None)
