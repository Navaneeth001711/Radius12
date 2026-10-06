"""Static reference data (categories, cities, mandals) and the initial
provider catalogue, transcribed from the mock DB in Radius.html so the
API serves the same demo data the original frontend shipped with."""

from extensions import db
from models import Provider, Review, Service

CATEGORIES = [
    {"id": "plumbing", "name": "Plumbing", "icon": "🔧"},
    {"id": "electrical", "name": "Electrical", "icon": "⚡"},
    {"id": "cleaning", "name": "Cleaning", "icon": "🧹"},
    {"id": "tutoring", "name": "Tutoring", "icon": "📚"},
    {"id": "salon", "name": "Salon & Grooming", "icon": "💇"},
    {"id": "painting", "name": "Painting", "icon": "🎨"},
    {"id": "appliance", "name": "Appliance Repair", "icon": "🔩"},
    {"id": "gardening", "name": "Gardening", "icon": "🌿"},
    {"id": "carpentry", "name": "Carpentry", "icon": "🪚"},
    {"id": "moving", "name": "Moving & Packing", "icon": "📦"},
    {"id": "pest", "name": "Pest Control", "icon": "🐜"},
    {"id": "fitness", "name": "Fitness Training", "icon": "🏋️"},
    {"id": "food", "name": "Food Service", "icon": "🍽️"},
    {"id": "phone", "name": "Phone Repair", "icon": "📱"},
]

AP_CITIES = [
    "Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Rajahmundry",
    "Kakinada", "Nellore", "Kurnool", "Anantapur", "Kadapa", "Eluru",
    "Vizianagaram", "Srikakulam", "Parvathipuram Manyam", "Anakapalli",
    "Alluri Sitharama Raju", "Konaseema", "West Godavari", "Krishna", "Palnadu",
    "Bapatla", "Prakasam", "Nandyal", "Sri Sathya Sai", "Annamayya", "Chittoor",
]

AP_MANDALS = {
    "Visakhapatnam": ["Visakhapatnam Urban", "Pendurthi", "Anandapuram", "Bheemunipatnam", "Gajuwaka"],
    "Vijayawada": ["Vijayawada Central", "Vijayawada Rural", "Penamaluru", "Gannavaram", "Ibrahimpatnam"],
    "Guntur": ["Guntur East", "Guntur West", "Pedakakani", "Tadikonda", "Mangalagiri"],
    "Tirupati": ["Tirupati Urban", "Tirupati Rural", "Renigunta", "Chandragiri", "Yerpedu"],
    "Rajahmundry": ["Rajahmundry Urban", "Rajahmundry Rural", "Kadiam", "Rangampeta", "Gokavaram"],
    "Kakinada": ["Kakinada Urban", "Kakinada Rural", "Pithapuram", "Samalkot", "Tallarevu"],
    "Nellore": ["Nellore Urban", "Nellore Rural", "Kovur", "Indukurpet", "Venkatachalam"],
    "Kurnool": ["Kurnool Urban", "Kurnool Rural", "Kallur", "Panyam", "Veldurthi"],
    "Anantapur": ["Anantapur Urban", "Anantapur Rural", "Kalyandurg", "Rayadurg", "Bukkarayasamudram"],
    "Kadapa": ["Kadapa Urban", "Kadapa Rural", "Vallur", "Chennur", "Mydukur"],
    "Eluru": ["Eluru Urban", "Eluru Rural", "Denduluru", "Pedavegi", "Nallajerla"],
    "Vizianagaram": ["Vizianagaram Urban", "Vizianagaram Rural", "Nellimarla", "Gajapathinagaram", "Bobbili"],
    "Srikakulam": ["Srikakulam Urban", "Etcherla", "Palasa", "Ponduru"],
    "Parvathipuram Manyam": ["Parvathipuram", "Salur", "Kurupam"],
    "Anakapalli": ["Anakapalli Urban", "Narsipatnam", "Yelamanchili"],
    "Alluri Sitharama Raju": ["Paderu", "Araku Valley", "Chintapalli"],
    "Konaseema": ["Amalapuram", "Razole", "Ravulapalem"],
    "West Godavari": ["Bhimavaram", "Tanuku", "Palakollu"],
    "Krishna": ["Machilipatnam", "Gudivada", "Avanigadda"],
    "Palnadu": ["Narasaraopet", "Sattenapalle", "Piduguralla"],
    "Bapatla": ["Bapatla Urban", "Chirala", "Repalle"],
    "Prakasam": ["Ongole", "Markapur", "Kandukur"],
    "Nandyal": ["Nandyal Urban", "Atmakur", "Dhone"],
    "Sri Sathya Sai": ["Puttaparthi", "Hindupur", "Dharmavaram"],
    "Annamayya": ["Rayachoti", "Rajampet", "Pileru"],
    "Chittoor": ["Chittoor Urban", "Punganur", "Palamaner"],
}

CITY_COORDS = {
    "Visakhapatnam": (17.6868, 83.2185), "Vijayawada": (16.5062, 80.6480),
    "Guntur": (16.3067, 80.4365), "Tirupati": (13.6288, 79.4192),
    "Rajahmundry": (17.0005, 81.8040), "Kakinada": (16.9891, 82.2475),
    "Nellore": (14.4426, 79.9865), "Kurnool": (15.8281, 78.0373),
    "Anantapur": (14.6819, 77.6006), "Kadapa": (14.4674, 78.8241),
    "Eluru": (16.7107, 81.0952), "Vizianagaram": (18.1067, 83.3956),
    "Srikakulam": (18.2949, 83.8938), "Parvathipuram Manyam": (18.7833, 83.4333),
    "Anakapalli": (17.691, 83.0037), "Alluri Sitharama Raju": (18.0762, 82.5527),
    "Konaseema": (16.5785, 82.0083), "West Godavari": (16.5449, 81.5212),
    "Krishna": (16.1875, 81.1389), "Palnadu": (16.2358, 80.0499),
    "Bapatla": (15.9046, 80.468), "Prakasam": (15.5057, 80.0499),
    "Nandyal": (15.4785, 78.483), "Sri Sathya Sai": (14.165, 77.809),
    "Annamayya": (14.05, 78.75), "Chittoor": (13.2172, 79.1003),
}

_STREET_NAMES = ["Main Road", "Temple Street", "Market Lane", "Ring Road", "Station Road"]


def category_info(category_id):
    return next((c for c in CATEGORIES if c["id"] == category_id), {"name": category_id, "icon": "🛠️"})


def mandals_for(city):
    return AP_MANDALS.get(city, [])


def jitter(base, seed_str):
    """Deterministic small offset so seeded providers get stable, spread-out
    map coordinates instead of all sitting on the exact city center."""
    h = 0
    for ch in seed_str:
        h = (h * 31 + ord(ch)) % 1000
    return base + ((h / 1000) - 0.5) * 0.06


_SEED_PROVIDERS = [
    {"id": "p1", "name": "Ramesh Chowdary", "phone": "+91 98481 23456", "category": "plumbing", "area": "Vijayawada",
     "bio": "Licensed plumber with nine years of experience fixing leaks, installing fixtures, and repiping older homes.",
     "reviewCount": 842,
     "services": [("Leak Repair", 300), ("Pipe Installation", 1200), ("Drain Cleaning", 450), ("Bathroom Fitting", 1800), ("Water Tank Cleaning", 600), ("Tap & Faucet Replacement", 350), ("Toilet Repair", 500), ("Motor Pump Fitting", 1500)],
     "reviews": [("Meera", 5, "Fixed my kitchen leak in under an hour.", "2026-06-02"), ("Santosh", 4, "Good work, arrived a bit later than planned.", "2026-05-18")]},
    {"id": "p9", "name": "SriSai Plumbing Works", "phone": "+91 90142 33445", "category": "plumbing", "area": "Visakhapatnam",
     "bio": "Emergency plumbing team available for same-day repairs across Vizag.", "reviewCount": 517,
     "services": [("Emergency Callout", 400), ("Water Heater Fix", 850), ("Sump Pump Install", 2200), ("Sewer Line Cleaning", 1300), ("Bore Well Pipe Fix", 1800)],
     "reviews": [("Divya", 5, "Came within the hour for a burst pipe.", "2026-06-10")]},
    {"id": "p2", "name": "Lakshmi Priya", "phone": "+91 93910 11223", "category": "electrical", "area": "Guntur",
     "bio": "Certified electrician specializing in home rewiring, panel upgrades, and lighting installs.", "reviewCount": 963,
     "services": [("Wiring Inspection", 400), ("Panel Upgrade", 3500), ("Light Fixture Install", 250), ("Ceiling Fan Install", 350), ("MCB & Fuse Repair", 300), ("Doorbell & Intercom Setup", 450)],
     "reviews": [("Ravi", 5, "Explained everything clearly before starting.", "2026-04-22"), ("Neha", 5, "Very tidy work, cleaned up after.", "2026-03-11")]},
    {"id": "p10", "name": "PowerFix Electricals", "phone": "+91 89851 66778", "category": "electrical", "area": "Rajahmundry",
     "bio": "Small team offering residential electrical repairs and smart home wiring.", "reviewCount": 288,
     "services": [("Outlet Repair", 250), ("Smart Switch Install", 450), ("Inverter Setup", 1500), ("CCTV Wiring", 2000), ("Stabilizer Install", 600)],
     "reviews": [("Tarun", 4, "Solid work, slightly pricier than expected.", "2026-05-02")]},
    {"id": "p3", "name": "CleanHome Services", "phone": "+91 91821 44556", "category": "cleaning", "area": "Vijayawada",
     "bio": "Residential cleaning crew offering weekly, biweekly, and one-time deep cleans.", "reviewCount": 1000,
     "services": [("Standard Clean", 500), ("Deep Clean", 900), ("Move-out Clean", 1400), ("Sofa & Carpet Clean", 750), ("Bathroom Deep Clean", 400), ("Balcony & Terrace Clean", 500)],
     "reviews": [("Farah", 5, "House looked spotless, will book again.", "2026-06-15"), ("Omkar", 4, "Good clean, missed a couple of spots.", "2026-05-29")]},
    {"id": "p11", "name": "Sparkle Cleaners AP", "phone": "+91 90001 22334", "category": "cleaning", "area": "Visakhapatnam",
     "bio": "Eco-friendly cleaning products used on every job, pet-safe and allergy-friendly.", "reviewCount": 604,
     "services": [("Standard Clean", 480), ("Deep Clean", 850), ("Kitchen Deep Clean", 650), ("Water Tank Cleaning", 550), ("Post-Construction Clean", 1600)],
     "reviews": [("Ishaan", 5, "Loved that they used non-toxic products.", "2026-06-01")]},
    {"id": "p4", "name": "Karthik Varma", "phone": "+91 88855 99001", "category": "tutoring", "area": "Guntur",
     "bio": "Math and physics tutor for high school and intermediate students, seven years teaching experience.", "reviewCount": 356,
     "services": [("Math Session (1hr)", 300), ("Physics Session (1hr)", 350), ("Exam Prep Package", 2500), ("Chemistry Session (1hr)", 350), ("Group Tuition (per student)", 200)],
     "reviews": [("Aditi", 5, "My grades improved within a month.", "2026-04-08")]},
    {"id": "p12", "name": "Divya Sree", "phone": "+91 87654 32109", "category": "tutoring", "area": "Tirupati",
     "bio": "English and language tutor focused on writing skills and conversational practice.", "reviewCount": 201,
     "services": [("English Session (1hr)", 280), ("Essay Coaching", 400), ("Spoken English Batch", 1500), ("Interview Prep", 500)],
     "reviews": [("Rohan", 4, "Patient and encouraging teaching style.", "2026-05-20")]},
    {"id": "p5", "name": "Glow Beauty Studio", "phone": "+91 96666 12121", "category": "salon", "area": "Vijayawada",
     "bio": "Home-visit salon services including haircuts, styling, and basic grooming.", "reviewCount": 729,
     "services": [("Haircut", 150), ("Styling", 300), ("Grooming Package", 500), ("Facial", 450), ("Manicure", 350), ("Pedicure", 400), ("Bridal Makeup", 3500), ("Beard Trim", 120)],
     "reviews": [("Simran", 5, "Great haircut, very professional.", "2026-06-05")]},
    {"id": "p6", "name": "Suresh Babu Painters", "phone": "+91 94901 55667", "category": "painting", "area": "Kakinada",
     "bio": "Interior and exterior painting contractor, free color consultation included.", "reviewCount": 412,
     "services": [("Single Room", 2500), ("Full Interior", 9000), ("Exterior Touch-up", 3000), ("Waterproofing", 5500), ("Texture Painting", 4200), ("Wood Polish", 1800)],
     "reviews": [("Leela", 4, "Neat lines, finished on schedule.", "2026-05-14")]},
    {"id": "p7", "name": "QuickFix Appliances", "phone": "+91 93481 77889", "category": "appliance", "area": "Nellore",
     "bio": "Repairs for washers, dryers, refrigerators, and dishwashers, most major brands.", "reviewCount": 678,
     "services": [("Diagnostic Visit", 300), ("Washer Repair", 900), ("Fridge Repair", 1100), ("AC Servicing", 650), ("Microwave Repair", 500), ("RO Water Purifier Service", 450), ("Chimney Cleaning", 700)],
     "reviews": [("Nikhil", 5, "Diagnosed the issue fast and had the part on hand.", "2026-06-12")]},
    {"id": "p8", "name": "GreenLeaf Gardeners", "phone": "+91 90142 99887", "category": "gardening", "area": "Anantapur",
     "bio": "Garden maintenance, lawn care, and seasonal planting for homes and small yards.", "reviewCount": 184,
     "services": [("Lawn Mowing", 300), ("Garden Cleanup", 700), ("Seasonal Planting", 900), ("Tree Trimming", 1100), ("Irrigation Setup", 1600), ("Potted Plant Care (monthly)", 500)],
     "reviews": [("Priyanka", 5, "Yard has never looked better.", "2026-05-30")]},
    {"id": "p13", "name": "Venkat Carpentry Works", "phone": "+91 91234 56780", "category": "carpentry", "area": "Vijayawada",
     "bio": "Custom furniture, door and window repair, modular kitchen woodwork.", "reviewCount": 333,
     "services": [("Furniture Repair", 400), ("Door Fitting", 900), ("Custom Cabinet", 4500), ("Window Frame Repair", 700), ("Modular Kitchen Unit", 6000), ("Bed Assembly", 600)],
     "reviews": [("Anil", 5, "Beautiful custom shelf, exactly what I wanted.", "2026-06-08")]},
    {"id": "p14", "name": "Andhra Movers & Packers", "phone": "+91 90909 12345", "category": "moving", "area": "Visakhapatnam",
     "bio": "Local and intercity household moving with careful packing and insured transport.", "reviewCount": 521,
     "services": [("Local Move (1BHK)", 3500), ("Local Move (2BHK)", 5500), ("Packing Only", 1200), ("Intercity Move", 9500), ("Office Relocation", 8000), ("Loading/Unloading Only", 1500)],
     "reviews": [("Swathi", 5, "Careful with fragile items, on time.", "2026-05-25")]},
    {"id": "p15", "name": "SafeHome Pest Control", "phone": "+91 89898 34567", "category": "pest", "area": "Guntur",
     "bio": "General pest control, termite treatment, and mosquito fogging for homes.", "reviewCount": 445,
     "services": [("General Pest Treatment", 800), ("Termite Treatment", 2200), ("Cockroach Control", 600), ("Mosquito Fogging", 700), ("Rodent Control", 900), ("Bed Bug Treatment", 1400)],
     "reviews": [("Bhavana", 4, "Effective, smell cleared up in a day.", "2026-06-03")]},
    {"id": "p16", "name": "Coach Manoj Fitness", "phone": "+91 93333 45678", "category": "fitness", "area": "Vijayawada",
     "bio": "Personal trainer offering home and outdoor sessions for strength and weight loss goals.", "reviewCount": 267,
     "services": [("Single Session", 400), ("Monthly Package (12 sessions)", 4000), ("Nutrition Consult", 500), ("Yoga Session", 350), ("Group Bootcamp (per person)", 250)],
     "reviews": [("Kiran", 5, "Structured plan, saw real progress in weeks.", "2026-05-16")]},
]


def seed_admin():
    """Create the default admin account if no admin exists yet."""
    from datetime import date

    from config import Config
    from models import User

    if User.query.filter_by(role="admin").first():
        return
    email = Config.ADMIN_EMAIL.strip().lower()
    admin = User.query.filter_by(email=email).first()
    if admin is None:
        admin = User(id="admin1", name="Radius Admin", email=email,
                     joined_at=date.today().isoformat())
        db.session.add(admin)
    admin.role = "admin"
    admin.set_password(Config.ADMIN_PASSWORD)
    db.session.commit()
    print(f"[Radius] Default admin created: {email} (change the password via ADMIN_PASSWORD)")


def seed_if_empty():
    """Populate the providers table with the original demo catalogue the
    very first time the app runs against a fresh database."""
    if Provider.query.count() > 0:
        return

    for idx, p in enumerate(_SEED_PROVIDERS):
        center = CITY_COORDS.get(p["area"], (16.5, 80.6))
        street = f"{_STREET_NAMES[idx % len(_STREET_NAMES)]} {10 + (idx % 40)}"
        mandal = (mandals_for(p["area"]) or [p["area"] + " Urban"])[0]
        pincode = "5" + str((20000 + (idx * 137) % 9000))[:5]

        provider = Provider(
            id=p["id"],
            owner_id=None,
            name=p["name"],
            phone=p["phone"],
            category=p["category"],
            categories=p["category"],
            area=p["area"],
            street=street,
            mandal=mandal,
            pincode=pincode,
            lat=jitter(center[0], p["id"] + "lat"),
            lng=jitter(center[1], p["id"] + "lng"),
            bio=p["bio"],
            review_count=p["reviewCount"],
        )
        db.session.add(provider)
        db.session.flush()

        for name, price in p["services"]:
            db.session.add(Service(provider_id=provider.id, name=name, price=price))
        for name, rating, comment, date in p["reviews"]:
            db.session.add(Review(provider_id=provider.id, name=name, rating=rating, comment=comment, date=date))

    db.session.commit()
