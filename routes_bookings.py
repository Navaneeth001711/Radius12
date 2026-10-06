import random
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from extensions import db
from models import Booking, Provider, Review
from utils import clean, get_current_user, login_required, next_numeric_id, valid_phone

bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")

# paid -> accepted -> in_progress -> completed (then a review moves it to 'reviewed')
VALID_TRANSITIONS = {"paid": "accepted", "accepted": "in_progress", "in_progress": "completed"}


def _next_booking_id():
    return f"BK-{next_numeric_id(Booking, 'BK-', start=1000, id_col=Booking.id)}"


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


def _can_access(user, booking):
    provider = db.session.get(Provider, booking.provider_id)
    is_customer = booking.user_id == user.id
    is_owning_worker = provider is not None and provider.owner_id == user.id
    return is_customer or is_owning_worker


@bp.route("", methods=["POST"])
@login_required
def create_booking():
    """Creates a booking and simulates payment in one step (mirrors
    submitBooking() + submitPayment()/submitCodBooking() + finalizeBooking()
    from the frontend, since there's no real payment gateway here)."""
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    provider = db.session.get(Provider, str(data.get("providerId", "")))
    if not provider or provider.active is False:
        return jsonify(error="Provider not found"), 404
    if provider.category == "phone":
        return jsonify(error="This listing is for information only and cannot be booked"), 400
    if provider.owner_id == user.id:
        return jsonify(error="You cannot book your own service"), 400

    for field in ("serviceName", "date", "time", "street", "mandal", "pincode", "paymentMethod"):
        if data.get(field) in (None, ""):
            return jsonify(error=f"{field} is required"), 400

    # Never trust the client's price: look it up from the provider's listing.
    service = next((s for s in provider.services if s.name == data["serviceName"]), None)
    if service is None:
        return jsonify(error="That service is not offered by this provider"), 400

    try:
        booking_day = datetime.strptime(str(data["date"]), "%Y-%m-%d").date()
        datetime.strptime(str(data["time"]), "%H:%M")
    except ValueError:
        return jsonify(error="Invalid date or time"), 400
    if booking_day < datetime.now().date():
        return jsonify(error="Booking date cannot be in the past"), 400

    payment_method = data["paymentMethod"]
    if payment_method not in ("card", "cod"):
        return jsonify(error="Invalid payment method"), 400

    card_last4 = None
    cod_phone = None
    if payment_method == "card":
        card_number = str(data.get("cardNumber", "")).strip()
        if not all([card_number, str(data.get("expiry", "")).strip(),
                    str(data.get("cvc", "")).strip(), str(data.get("nameOnCard", "")).strip()]):
            return jsonify(error="Please fill in all payment fields"), 400
        digits = "".join(ch for ch in card_number if ch.isdigit())
        if len(digits) < 12:
            return jsonify(error="Please enter a valid card number"), 400
        card_last4 = digits[-4:]
        paid = True
    else:
        cod_phone = clean(data.get("codPhone"), 20)
        if not valid_phone(cod_phone):
            return jsonify(error="Please provide a valid contact number"), 400
        paid = False

    street = clean(data["street"], 200)
    mandal = clean(data["mandal"], 100)
    pincode = clean(data["pincode"], 10)
    address = f"{street}, {mandal} - {pincode}"
    booking = Booking(
        id=_next_booking_id(),
        user_id=user.id,
        provider_id=provider.id,
        service_name=service.name,
        service_price=service.price,
        date=data["date"],
        time=data["time"],
        street=street,
        mandal=mandal,
        pincode=pincode,
        address=address,
        notes=clean(data.get("notes"), 500),
        payment_method=payment_method,
        card_last4=card_last4,
        cod_phone=cod_phone,
        paid=paid,
        stage="paid",
        created_at=_now(),
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking=booking.to_dict()), 201


@bp.route("", methods=["GET"])
@login_required
def list_my_bookings():
    """Bookings made BY the current user (as a customer)."""
    user = get_current_user()
    bookings = (
        Booking.query.filter_by(user_id=user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return jsonify(bookings=[b.to_dict() for b in bookings])


@bp.route("/provider/mine", methods=["GET"])
@login_required
def list_provider_bookings():
    """Bookings received BY the current user's provider profile (worker dashboard)."""
    user = get_current_user()
    provider = Provider.query.filter_by(owner_id=user.id).first()
    if not provider:
        return jsonify(error="No provider profile found for this account"), 404
    bookings = (
        Booking.query.filter_by(provider_id=provider.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return jsonify(bookings=[b.to_dict() for b in bookings])


@bp.route("/<booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id):
    user = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify(error="Booking not found"), 404
    if not _can_access(user, booking):
        return jsonify(error="Not authorized"), 403
    return jsonify(booking=booking.to_dict())


@bp.route("/<booking_id>/stage", methods=["PATCH"])
@login_required
def advance_stage(booking_id):
    """Advances a booking to the next stage. Mirrors advanceStage() — in the
    original demo this button is on the customer's status page ('Simulate:
    Provider Accepts' etc); here any party with access to the booking may
    call it, same as the demo allows."""
    user = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify(error="Booking not found"), 404
    if not _can_access(user, booking):
        return jsonify(error="Not authorized"), 403

    new_stage = (request.get_json(silent=True) or {}).get("stage")
    if VALID_TRANSITIONS.get(booking.stage) != new_stage:
        return jsonify(error=f"Cannot move from '{booking.stage}' to '{new_stage}'"), 400

    booking.stage = new_stage
    if new_stage == "in_progress":
        eta = 8 + random.randint(0, 9)
        booking.tracking_eta = eta
        booking.tracking_eta_initial = eta
    db.session.commit()
    return jsonify(booking=booking.to_dict())


@bp.route("/<booking_id>/tracking/tick", methods=["POST"])
@login_required
def tick_tracking(booking_id):
    """Decrements the live-tracking ETA by one minute. The frontend polled
    this automatically every few seconds via setInterval; call it the same
    way from a client-side timer."""
    user = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify(error="Booking not found"), 404
    if not _can_access(user, booking):
        return jsonify(error="Not authorized"), 403

    if booking.stage == "in_progress" and (booking.tracking_eta or 0) > 0:
        booking.tracking_eta -= 1
        db.session.commit()
    return jsonify(booking=booking.to_dict())


@bp.route("/<booking_id>/review", methods=["POST"])
@login_required
def submit_review(booking_id):
    user = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.user_id != user.id:
        return jsonify(error="Booking not found"), 404
    if booking.stage != "completed":
        return jsonify(error="This booking isn't ready for a review yet"), 400

    data = request.get_json(silent=True) or {}
    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        rating = 0
    comment = clean(data.get("comment"), 1000)
    if not (1 <= rating <= 5):
        return jsonify(error="Please select a star rating"), 400
    if not comment:
        return jsonify(error="Please add a comment"), 400

    provider = db.session.get(Provider, booking.provider_id)
    if provider is None:
        return jsonify(error="Provider no longer exists"), 404
    review = Review(
        provider_id=provider.id,
        name=user.name,
        rating=rating,
        comment=comment,
        date=datetime.now().date().isoformat(),
    )
    db.session.add(review)
    provider.review_count = (provider.review_count or len(provider.reviews)) + 1
    booking.stage = "reviewed"
    db.session.commit()

    return jsonify(booking=booking.to_dict(), review=review.to_dict())
