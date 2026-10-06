from flask import Blueprint, jsonify, request

from extensions import db
from models import Provider, Service
from seed import AP_CITIES
from utils import clean, get_current_user, login_required, valid_phone

bp = Blueprint("profile", __name__, url_prefix="/api/profile")


def _serialize(user):
    provider = Provider.query.filter_by(owner_id=user.id).first() if user.role == "worker" else None
    return jsonify(
        user=user.to_dict(),
        provider=provider.to_dict(include_details=True) if provider else None,
    )


@bp.route("", methods=["GET"])
@login_required
def get_profile():
    return _serialize(get_current_user())


@bp.route("", methods=["PUT"])
@login_required
def update_profile():
    """Mirrors saveProfile(): updates the account's own fields, and — for a
    worker — their public provider listing (bio, street, services)."""
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    if data.get("name"):
        user.name = clean(data["name"], 100)
    if data.get("phone"):
        if not valid_phone(data["phone"]):
            return jsonify(error="Please enter a valid phone number"), 400
        user.phone = clean(data["phone"], 20)
    if data.get("city"):
        if data["city"] not in AP_CITIES:
            return jsonify(error="Please select a valid city"), 400
        user.city = data["city"]
    if data.get("mandal"):
        user.mandal = clean(data["mandal"], 100)
    if "street" in data:
        user.street = clean(data["street"], 200)
    if "pincode" in data:
        user.pincode = clean(data["pincode"], 10)

    if "avatarUrl" in data:
        avatar = data["avatarUrl"] or None
        if avatar and (not str(avatar).startswith("data:image/") or len(avatar) > 3_000_000):
            return jsonify(error="Invalid or too large image"), 400
        user.avatar_url = avatar

    if user.role == "worker":
        provider = Provider.query.filter_by(owner_id=user.id).first()
        if provider:
            # Keep the public listing in sync with the account.
            provider.name = user.name
            provider.phone = user.phone
            provider.area = user.city
            provider.mandal = user.mandal
            if user.street:
                provider.street = user.street
            if user.pincode:
                provider.pincode = user.pincode
            if data.get("bio"):
                provider.bio = clean(data["bio"], 1000)
            if data.get("services") is not None:
                new_services = []
                for s in data["services"]:
                    name = clean(s.get("name"), 100)
                    try:
                        price = int(s.get("price"))
                    except (TypeError, ValueError):
                        continue
                    if name and price >= 0:
                        new_services.append((name, price))
                if new_services:
                    Service.query.filter_by(provider_id=provider.id).delete()
                    for name, price in new_services:
                        db.session.add(Service(provider_id=provider.id, name=name, price=price))

    db.session.commit()
    return _serialize(user)
