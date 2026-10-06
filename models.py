from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)  # e.g. "u1"
    role = db.Column(db.String, nullable=False, default="customer")  # customer | worker | admin
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    phone = db.Column(db.String)
    city = db.Column(db.String)
    mandal = db.Column(db.String)
    password_hash = db.Column(db.String, nullable=False)
    avatar_url = db.Column(db.Text)  # data URL or hosted image URL
    street = db.Column(db.String)
    pincode = db.Column(db.String)
    joined_at = db.Column(db.String)
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # admin can suspend

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "mandal": self.mandal,
            "avatarUrl": self.avatar_url,
            "street": self.street,
            "pincode": self.pincode,
            "joinedAt": self.joined_at,
            "isActive": self.is_active is not False,
        }


class Provider(db.Model):
    __tablename__ = "providers"

    id = db.Column(db.String, primary_key=True)  # e.g. "p1" or "p17_u5"
    owner_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    category = db.Column(db.String, nullable=False)  # primary category id
    categories = db.Column(db.String)  # comma-separated category ids
    area = db.Column(db.String)  # city
    street = db.Column(db.String)
    mandal = db.Column(db.String)
    pincode = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    bio = db.Column(db.Text)
    review_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)  # admin can hide a listing

    owner = db.relationship("User", foreign_keys=[owner_id], lazy=True)
    services = db.relationship(
        "Service", backref="provider", cascade="all, delete-orphan", lazy=True
    )
    reviews = db.relationship(
        "Review", backref="provider", cascade="all, delete-orphan", lazy=True
    )

    def avg_rating(self):
        if not self.reviews:
            return 0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    def to_dict(self, include_details=False):
        data = {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "category": self.category,
            "categories": (self.categories or self.category).split(","),
            "area": self.area,
            "street": self.street,
            "mandal": self.mandal,
            "pincode": self.pincode,
            "lat": self.lat,
            "lng": self.lng,
            "bio": self.bio,
            "reviewCount": self.review_count or len(self.reviews),
            "avgRating": round(self.avg_rating(), 2),
            "ownerId": self.owner_id,
            "avatarUrl": self.owner.avatar_url if self.owner else None,
            "active": self.active is not False,
        }
        if include_details:
            data["services"] = [s.to_dict() for s in self.services]
            data["reviews"] = [r.to_dict() for r in self.reviews]
        return data


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_id = db.Column(db.String, db.ForeignKey("providers.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"name": self.name, "price": self.price}


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_id = db.Column(db.String, db.ForeignKey("providers.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rating": self.rating,
            "comment": self.comment,
            "date": self.date,
        }


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.String, primary_key=True)  # e.g. "BK-1001"
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    provider_id = db.Column(db.String, db.ForeignKey("providers.id"), nullable=False)

    service_name = db.Column(db.String, nullable=False)
    service_price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)

    street = db.Column(db.String)
    mandal = db.Column(db.String)
    pincode = db.Column(db.String)
    address = db.Column(db.String)
    notes = db.Column(db.Text)

    payment_method = db.Column(db.String, nullable=False)  # card | cod
    card_last4 = db.Column(db.String)
    cod_phone = db.Column(db.String)
    paid = db.Column(db.Boolean, default=False)

    # paid -> accepted -> in_progress -> completed -> reviewed
    stage = db.Column(db.String, nullable=False, default="paid")
    created_at = db.Column(db.String)

    tracking_eta = db.Column(db.Integer)
    tracking_eta_initial = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "providerId": self.provider_id,
            "serviceName": self.service_name,
            "servicePrice": self.service_price,
            "date": self.date,
            "time": self.time,
            "street": self.street,
            "mandal": self.mandal,
            "pincode": self.pincode,
            "address": self.address,
            "notes": self.notes,
            "paymentMethod": self.payment_method,
            "cardLast4": self.card_last4,
            "codPhone": self.cod_phone,
            "paid": self.paid,
            "stage": self.stage,
            "createdAt": self.created_at,
            "trackingETA": self.tracking_eta,
            "trackingETAInitial": self.tracking_eta_initial,
        }
