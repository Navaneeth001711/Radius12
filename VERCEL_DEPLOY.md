# Radius - Vercel Deployment

This copy is prepared for Vercel.

## What was fixed
- Added a root `app.py` entrypoint so Vercel can detect the Flask application.
- Added a root `requirements.txt` copied from `backend/requirements.txt`.
- Kept the existing `frontend/` + `backend/` structure unchanged.

## Important: database
The app uses `DATABASE_URL`. For Vercel, set `DATABASE_URL` to a hosted PostgreSQL database (for example Neon). Do NOT rely on the local SQLite default for production data.

Also set:
- `SECRET_KEY` = a long random value
- `ADMIN_EMAIL` = your admin email
- `ADMIN_PASSWORD` = a strong admin password
- `SESSION_COOKIE_SECURE` = `1`

## Deploy
1. Upload/push the contents of this ZIP to GitHub.
2. In Vercel, import the GitHub repository.
3. Keep the project root at the repository root.
4. Add the environment variables above.
5. Deploy.
6. Test: `https://YOUR-DOMAIN/api/health` — it should return `{"status":"ok"}`.
7. Open `https://YOUR-DOMAIN/Radius.html`.

The project still contains the original Render files; Vercel can ignore them.
