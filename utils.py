import html
import re
from functools import wraps

from flask import jsonify, session

from extensions import db
from models import User


def get_current_user():
    """Returns the logged-in, active User, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if user is None or user.is_active is False:
        session.pop("user_id", None)
        return None
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_current_user():
            return jsonify(error="Please log in to continue"), 401
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify(error="Please log in to continue"), 401
        if user.role != "admin":
            return jsonify(error="Admin access required"), 403
        return fn(*args, **kwargs)

    return wrapper


def clean(value, max_len=500):
    """Trim + HTML-escape user text. The frontend renders many fields with
    innerHTML, so escaping on the way in prevents stored XSS."""
    if value is None:
        return ""
    return html.escape(str(value).strip(), quote=True)[:max_len]


def next_numeric_id(model, prefix, start=0, id_col=None):
    """max(existing numeric part after `prefix`) + 1. Unlike count()+1 this
    never collides after a row is deleted (the admin portal can delete rows)."""
    col = id_col if id_col is not None else model.id
    pattern = re.compile(r"^" + re.escape(prefix) + r"(\d+)")
    best = start
    for (value,) in db.session.query(col).all():
        match = pattern.match(str(value))
        if match:
            best = max(best, int(match.group(1)))
    return best + 1


def valid_phone(value):
    digits = re.sub(r"\D", "", str(value or ""))
    return len(digits) >= 10


def valid_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", str(value or "")))
