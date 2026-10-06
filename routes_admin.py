"""Admin portal API. Every route requires a logged-in user with role 'admin'."""
from collections import Counter

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from extensions import db
from models import Booking, Provider, Review, Service, User
from seed import AP_CITIES, CATEGORIES
from utils import admin_required, clean, get_current_user, valid_email, valid_phone

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

STAGES = ["paid", "accepted", "in_progress", "completed", "reviewed"]
ROLES = ["customer", "worker", "admin"]
CATEGORY_IDS = {c["id"] for c in CATEGORIES}


def _body():
    return request.get_json(silent=True) or {}


def _like(q):
    return f"%{q.strip().lower()}%"


# ---------------------------------------------------------------- stats
@bp.route("/stats")
@admin_required
def stats():
    bookings = Booking.query.all()
    by_stage = Counter(b.stage for b in bookings)
    revenue_paid = sum(b.service_price for b in bookings if b.paid)
    revenue_cod_pending = sum(b.service_price for b in bookings if not b.paid and b.stage not in ("completed", "reviewed"))
    revenue_total = sum(b.service_price for b in bookings if b.stage in ("completed", "reviewed"))

    providers = {p.id: p for p in Provider.query.all()}
    by_category = Counter()
    for b in bookings:
        p = providers.get(b.provider_id)
        if p:
            by_category[p.category] += 1

    recent = Booking.query.order_by(Booking.created_at.desc()).limit(8).all()
    users = {u.id: u for u in User.query.all()}
    return jsonify(
        counts={
            "users": User.query.count(),
            "customers": User.query.filter_by(role="customer").count(),
            "workers": User.query.filter_by(role="worker").count(),
            "admins": User.query.filter_by(role="admin").count(),
            "suspended": User.query.filter(User.is_active.is_(False)).count(),
            "providers": len(providers),
            "hiddenProviders": sum(1 for p in providers.values() if p.active is False),
            "bookings": len(bookings),
            "reviews": Review.query.count(),
        },
        revenue={"collectedOnline": revenue_paid, "codPending": revenue_cod_pending, "completedValue": revenue_total},
        bookingsByStage={s: by_stage.get(s, 0) for s in STAGES},
        bookingsByCategory=[{"category": c, "count": n} for c, n in by_category.most_common()],
        recentBookings=[
            {
                **b.to_dict(),
                "customerName": users[b.user_id].name if b.user_id in users else "(deleted)",
                "providerName": providers[b.provider_id].name if b.provider_id in providers else "(deleted)",
            }
            for b in recent
        ],
    )


# ---------------------------------------------------------------- users
@bp.route("/users")
@admin_required
def list_users():
    q = (request.args.get("q") or "").strip()
    role = request.args.get("role")
    query = User.query
    if role in ROLES:
        query = query.filter_by(role=role)
    if q:
        like = _like(q)
        query = query.filter(or_(db.func.lower(User.name).like(like), db.func.lower(User.email).like(like),
                                 db.func.lower(User.phone).like(like), db.func.lower(User.city).like(like)))
    users = query.order_by(User.joined_at.desc(), User.id.desc()).all()
    counts = Counter(b.user_id for b in Booking.query.all())
    return jsonify(users=[{**u.to_dict(), "bookingCount": counts.get(u.id, 0)} for u in users])


@bp.route("/users/<user_id>", methods=["PATCH"])
@admin_required
def update_user(user_id):
    me = get_current_user()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(error="User not found"), 404
    data = _body()

    if "name" in data:
        if not str(data["name"]).strip():
            return jsonify(error="Name cannot be empty"), 400
        user.name = clean(data["name"], 100)
    if "email" in data:
        email = str(data["email"]).strip().lower()
        if not valid_email(email):
            return jsonify(error="Invalid email"), 400
        clash = User.query.filter(User.email == email, User.id != user.id).first()
        if clash:
            return jsonify(error="Another account already uses that email"), 409
        user.email = email
    if "phone" in data and data["phone"]:
        if not valid_phone(data["phone"]):
            return jsonify(error="Invalid phone number"), 400
        user.phone = clean(data["phone"], 20)
    if "city" in data and data["city"]:
        if data["city"] not in AP_CITIES:
            return jsonify(error="Invalid city"), 400
        user.city = data["city"]
    if "mandal" in data:
        user.mandal = clean(data["mandal"], 100)

    if "role" in data and data["role"] != user.role:
        if data["role"] not in ROLES:
            return jsonify(error="Invalid role"), 400
        if user.id == me.id:
            return jsonify(error="You cannot change your own role"), 400
        if user.role == "worker" and Provider.query.filter_by(owner_id=user.id).first():
            return jsonify(error="This user owns a provider listing. Delete or reassign the listing first."), 400
        user.role = data["role"]

    if "isActive" in data:
        if user.id == me.id and not data["isActive"]:
            return jsonify(error="You cannot suspend your own account"), 400
        user.is_active = bool(data["isActive"])
        provider = Provider.query.filter_by(owner_id=user.id).first()
        if provider:  # hide a suspended worker's listing from customers
            provider.active = bool(data["isActive"])

    if data.get("newPassword"):
        if len(str(data["newPassword"])) < 6:
            return jsonify(error="Password must be at least 6 characters"), 400
        user.set_password(str(data["newPassword"]))

    db.session.commit()
    return jsonify(user=user.to_dict())


@bp.route("/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    me = get_current_user()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(error="User not found"), 404
    if user.id == me.id:
        return jsonify(error="You cannot delete your own account"), 400
    if Booking.query.filter_by(user_id=user.id).first():
        return jsonify(error="This user has bookings. Suspend the account instead of deleting it."), 400
    provider = Provider.query.filter_by(owner_id=user.id).first()
    if provider:
        if Booking.query.filter_by(provider_id=provider.id).first():
            return jsonify(error="This worker's listing has bookings. Suspend the account instead."), 400
        db.session.delete(provider)
    db.session.delete(user)
    db.session.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------ providers
@bp.route("/providers")
@admin_required
def list_providers():
    q = (request.args.get("q") or "").strip()
    category = request.args.get("category")
    query = Provider.query
    if q:
        like = _like(q)
        query = query.filter(or_(db.func.lower(Provider.name).like(like), db.func.lower(Provider.area).like(like),
                                 db.func.lower(Provider.phone).like(like)))
    providers = query.order_by(Provider.name).all()
    if category:
        providers = [p for p in providers if category in (p.categories or p.category).split(",")]
    counts = Counter(b.provider_id for b in Booking.query.all())
    return jsonify(providers=[{**p.to_dict(include_details=True), "bookingCount": counts.get(p.id, 0)} for p in providers])


@bp.route("/providers/<provider_id>", methods=["PATCH"])
@admin_required
def update_provider(provider_id):
    p = db.session.get(Provider, provider_id)
    if not p:
        return jsonify(error="Provider not found"), 404
    data = _body()

    for field, attr, limit in (("name", "name", 100), ("bio", "bio", 1000), ("street", "street", 200),
                               ("mandal", "mandal", 100), ("pincode", "pincode", 10)):
        if field in data:
            val = clean(data[field], limit)
            if field == "name" and not val:
                return jsonify(error="Name cannot be empty"), 400
            setattr(p, attr, val)
    if "phone" in data:
        if not valid_phone(data["phone"]):
            return jsonify(error="Invalid phone number"), 400
        p.phone = clean(data["phone"], 20)
    if "area" in data:
        if data["area"] not in AP_CITIES:
            return jsonify(error="Invalid city"), 400
        p.area = data["area"]
    if "categories" in data:
        cats = [c for c in (data["categories"] or []) if c in CATEGORY_IDS]
        if not cats:
            return jsonify(error="Select at least one valid category"), 400
        p.category = cats[0]
        p.categories = ",".join(cats)
    if "active" in data:
        p.active = bool(data["active"])

    if "services" in data:
        new_services = []
        for s in data["services"] or []:
            name = clean(s.get("name"), 100)
            try:
                price = int(s.get("price"))
            except (TypeError, ValueError):
                continue
            if name and price >= 0:
                new_services.append((name, price))
        if not new_services:
            return jsonify(error="A provider needs at least one service with a price"), 400
        Service.query.filter_by(provider_id=p.id).delete()
        for name, price in new_services:
            db.session.add(Service(provider_id=p.id, name=name, price=price))

    # keep the owning worker's account in sync with the public listing
    owner = db.session.get(User, p.owner_id) if p.owner_id else None
    if owner:
        owner.name, owner.phone, owner.city, owner.mandal = p.name, p.phone, p.area, p.mandal

    db.session.commit()
    db.session.refresh(p)
    return jsonify(provider=p.to_dict(include_details=True))


@bp.route("/providers/<provider_id>", methods=["DELETE"])
@admin_required
def delete_provider(provider_id):
    p = db.session.get(Provider, provider_id)
    if not p:
        return jsonify(error="Provider not found"), 404
    if Booking.query.filter_by(provider_id=p.id).first():
        return jsonify(error="This provider has bookings. Hide the listing instead of deleting it."), 400
    db.session.delete(p)
    db.session.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------- bookings
@bp.route("/bookings")
@admin_required
def list_bookings():
    stage = request.args.get("stage")
    q = (request.args.get("q") or "").strip().lower()
    query = Booking.query
    if stage in STAGES:
        query = query.filter_by(stage=stage)
    bookings = query.order_by(Booking.created_at.desc()).all()
    users = {u.id: u for u in User.query.all()}
    providers = {p.id: p for p in Provider.query.all()}
    rows = []
    for b in bookings:
        row = {
            **b.to_dict(),
            "customerName": users[b.user_id].name if b.user_id in users else "(deleted)",
            "customerEmail": users[b.user_id].email if b.user_id in users else "",
            "providerName": providers[b.provider_id].name if b.provider_id in providers else "(deleted)",
        }
        if q and q not in " ".join(str(row[k]) for k in ("id", "customerName", "providerName", "serviceName")).lower():
            continue
        rows.append(row)
    return jsonify(bookings=rows)


@bp.route("/bookings/<booking_id>", methods=["PATCH"])
@admin_required
def update_booking(booking_id):
    b = db.session.get(Booking, booking_id)
    if not b:
        return jsonify(error="Booking not found"), 404
    data = _body()
    if "stage" in data:
        if data["stage"] not in STAGES:
            return jsonify(error="Invalid stage"), 400
        b.stage = data["stage"]
        if b.stage in ("paid", "accepted"):
            b.tracking_eta = b.tracking_eta_initial = None
    if "paid" in data:
        b.paid = bool(data["paid"])
    db.session.commit()
    return jsonify(booking=b.to_dict())


@bp.route("/bookings/<booking_id>", methods=["DELETE"])
@admin_required
def delete_booking(booking_id):
    b = db.session.get(Booking, booking_id)
    if not b:
        return jsonify(error="Booking not found"), 404
    db.session.delete(b)
    db.session.commit()
    return jsonify(ok=True)


# -------------------------------------------------------------- reviews
@bp.route("/reviews")
@admin_required
def list_reviews():
    providers = {p.id: p.name for p in Provider.query.all()}
    reviews = Review.query.order_by(Review.date.desc(), Review.id.desc()).all()
    return jsonify(reviews=[{**r.to_dict(), "providerId": r.provider_id,
                             "providerName": providers.get(r.provider_id, "(deleted)")} for r in reviews])


@bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@admin_required
def delete_review(review_id):
    r = db.session.get(Review, review_id)
    if not r:
        return jsonify(error="Review not found"), 404
    provider = db.session.get(Provider, r.provider_id)
    if provider and (provider.review_count or 0) > 0:
        provider.review_count -= 1
    db.session.delete(r)
    db.session.commit()
    return jsonify(ok=True)
