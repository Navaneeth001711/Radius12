from flask import Blueprint, jsonify, request

from extensions import db
from models import Provider
from seed import AP_CITIES, AP_MANDALS, CATEGORIES

bp = Blueprint("providers", __name__, url_prefix="/api")


@bp.route("/categories")
def categories():
    return jsonify(categories=CATEGORIES)


@bp.route("/cities")
def cities():
    return jsonify(cities=AP_CITIES, mandals=AP_MANDALS)


@bp.route("/providers")
def list_providers():
    """List/search providers. Query params:
    category, city, mandal, q (free-text search), sort ('rating' | 'reviews')
    """
    category = request.args.get("category") or None
    city = request.args.get("city") or None
    mandal = request.args.get("mandal") or None
    query_text = (request.args.get("q") or "").strip().lower()
    sort_by = request.args.get("sort", "rating")

    providers = Provider.query.filter(Provider.active.isnot(False)).all()
    results = []
    for p in providers:
        if category and category not in (p.categories or p.category).split(","):
            continue
        if city and p.area != city:
            continue
        if mandal and p.mandal != mandal:
            continue
        if query_text:
            haystack = " ".join(
                [p.name, p.category, p.area or "", p.bio or ""]
                + [s.name for s in p.services]
            ).lower()
            if query_text not in haystack:
                continue
        results.append(p)

    if sort_by == "reviews":
        results.sort(key=lambda p: (p.review_count or len(p.reviews)), reverse=True)
    else:
        results.sort(key=lambda p: p.avg_rating(), reverse=True)

    # include_details=True so the list view has services (for "from ₹X")
    # and reviews (for avgRating()) without a second round-trip per card.
    return jsonify(providers=[p.to_dict(include_details=True) for p in results])


@bp.route("/providers/<provider_id>")
def get_provider(provider_id):
    provider = db.session.get(Provider, provider_id)
    if not provider or provider.active is False:
        return jsonify(error="Provider not found"), 404
    return jsonify(provider=provider.to_dict(include_details=True))
