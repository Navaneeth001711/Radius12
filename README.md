# Radius — Local Service Finder (Working Local Package)

This package contains the Radius frontend and Flask backend configured to run together locally.

## Windows — easiest way

1. Install Python 3.10 or newer.
2. Double-click **start_windows.bat**.
3. The first run installs the required Flask packages.
4. Open **http://127.0.0.1:5500/Radius.html** in your browser.

The launcher starts:
- Frontend: `http://127.0.0.1:5500/Radius.html`
- Backend health check: `http://127.0.0.1:5000/api/health`

The SQLite database is created automatically at `backend/radius.db` and demo providers are seeded on first startup.

## Linux / macOS

Run:

```bash
./start_linux_mac.sh
```

Then open `http://127.0.0.1:5500/Radius.html`.

## Admin portal

Open **http://127.0.0.1:5500/admin.html** (or click *Admin Portal* in the site navbar after logging in as admin).

Default login (created automatically on first start):

- Email: `admin@radius.local`
- Password: `admin123`

**Change these** by setting the `ADMIN_EMAIL` / `ADMIN_PASSWORD` environment variables *before the first run* (see `backend/.env.example`), or by editing the admin user's password from the Users page.

The portal lets an admin:

- View a dashboard (users, workers, listings, bookings, revenue, bookings by stage/category)
- **Users** — search, edit details, change role, reset password, suspend/activate, delete
- **Providers** — edit profile, categories and services/prices, hide/show a listing, delete
- **Bookings** — filter/search, change stage, delete
- **Reviews** — moderate (delete) reviews

Safety rules: you can't suspend/delete/demote your own account, and users/providers that have bookings can be suspended or hidden but not deleted.

## Fixes in this version

- Login cookie bug: the page was served from `127.0.0.1` but called the API at `localhost`, so the session cookie was never sent. The API host now follows the page's host.
- Booking price is now looked up on the server (clients could previously send any price); past dates, bad times, fake provider/service names and bookings of "information only" listings are rejected.
- Stored XSS: user-entered text (names, bios, reviews, notes, services) is escaped on the server.
- ID generation used `count()+1` and could collide after deletions; now uses max+1.
- Customer street/pincode were never saved; worker listing name/phone/photo/city now stay in sync with the account.
- Worker registration form no longer wipes typed fields when you pick a category or add a service row.
- Missing categories (Food, Phone Repair) and cities/mandals added to the backend; worker pins now land in the right city.
- Crashes fixed when a provider has no services or has been removed; password minimum raised to 6; input validation for email/phone/city; JSON error pages; existing `radius.db` files are upgraded automatically.

## Included functionality

- Customer registration/login/logout
- Worker registration and provider listing
- Provider search/filtering
- Service details
- Booking creation
- Simulated card/COD payment flow
- Booking status progression
- Tracking ETA simulation
- Reviews
- Customer/worker profiles
- SQLite persistence

Payments are simulated; this package does not charge real cards.

## Deploy (Render, free)

1. Create a GitHub repo and push this folder (`git init`, `git add .`, `git commit`, `git push`).
2. On https://render.com choose **New + > Blueprint**, select the repo. `render.yaml` creates the web service and a Postgres database.
3. When asked, enter a strong `ADMIN_PASSWORD` (and change `ADMIN_EMAIL` in the dashboard if you like).
4. After the build finishes open `https://<your-service>.onrender.com` (admin: `/admin.html`).

Notes: the free web service sleeps when idle (first load is slow) and the free Postgres database expires after about 30 days; upgrade the plan for a real site. Payments are still simulated.
