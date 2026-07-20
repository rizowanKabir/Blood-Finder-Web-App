# 🩸 Blood Finder

A full-stack Django web application connecting blood donors with people who need them —
donor directory with search/filters, blood request board with an accept/complete workflow,
notifications, a personal dashboard, and a premium pink + cyan glassmorphism UI.

Built and tested end-to-end with **Django 6.0.7** on **Python 3.12** (forward-compatible with 3.13+).

---

## 1. Quick Start

```bash
# 1. Clone / unzip, then enter the project
cd bloodfinder

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) copy environment config — defaults already work for local dev
cp .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Create your own admin account
python manage.py createsuperuser

# 7. (Optional but recommended) seed realistic demo data
python manage.py seed_demo_data --donors 24 --requests 15
# Seeded users all use the password: DemoPass123

# 8. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the site and **http://127.0.0.1:8000/admin/** for the admin panel.

---

## 2. What's Implemented

| Area | Details |
|---|---|
| **Auth** | Register, login/logout (email-based login), forgot/reset password, change password, email verification (console-logged in dev) |
| **Donor directory** | Search/filter by blood group, division, district, area, availability; instant live preview on the homepage; full paginated results page |
| **Blood requests** | Post a request, browse/filter open requests, **Accept** (donor claims it) → **Complete** (marks donation done, auto-increments the donor's donation count) |
| **Notifications** | Donors are automatically notified when a new request matches their blood group; requesters are notified when a donor accepts |
| **Dashboard** | Profile completion %, donor status toggle, My Requests / My Donations tabs, notifications inbox, edit profile, change password |
| **Admin** | Full Django admin (Users, Donors, Requests, Testimonials, FAQs, Contact Messages) + a separate staff-only **Admin Stats** page with live Chart.js charts |
| **API** | Read-only DRF endpoints at `/api/donors/` and `/api/requests/` — a starting point for a future mobile app or integration |
| **UI** | Pink/cyan gradient glassmorphism theme, dark mode (persisted), sticky navbar, scroll-reveal animations, animated counters, toast notifications, image upload preview, responsive tables, pagination |
| **Tests** | 27 tests across all 5 apps — models, auth, permissions, and the full accept → complete donation workflow. All passing (`python manage.py test`). |

---

## 3. Project Structure

```
bloodfinder/
├── bloodfinder/          # Project settings, root urls.py
├── core/                 # Home, About, Privacy, Terms, Contact, Testimonials, FAQ
├── accounts/             # Custom User model, register/login/logout, password reset, email verification
├── donors/               # Donor model, directory search, become-a-donor, DRF API
├── blood_requests/       # BloodRequest model, request board, accept/complete workflow, notify signal
├── dashboard/            # Notification model, dashboard home, my activity, admin stats
├── templates/            # base.html + per-app templates (server-rendered, no SPA framework)
├── static/
│   ├── css/               # style.css (theme), animations.css
│   └── js/                 # theme.js, main.js, counters.js, search.js, validation.js, admin-charts.js
├── media/                 # User-uploaded profile pictures (created at runtime)
├── build.sh               # Render build script (install → collectstatic → migrate → create_admin)
├── render.yaml             # Render Blueprint — one-click deploy (web service + free Postgres)
└── .python-version         # Pins the Python version for Render's build
```

### Notable design decisions (and why)

- **`requests/` app renamed to `blood_requests/` internally.** The original spec's app name
  `requests` collides with the extremely common `requests` HTTP library — importing it anywhere
  in the project would shadow the real package. All **URLs** are still exactly `/requests/...`
  as specified; only the internal Python package name changed.
- **Email as the login field**, not a separate username, via a custom `AbstractUser` subclass
  with `USERNAME_FIELD = 'email'`. Verified working end-to-end (see `accounts/tests.py`).
- **One avatar per account** (`User.profile_picture`) instead of separate donor/user pictures,
  so there's a single source of truth shown consistently in the navbar, dashboard, and donor cards.
- **"Featured Donors" and "Recently Joined Donors" are one combined showcase** on the homepage
  (featured first, then most recent) rather than two near-identical grids back to back.
- **"My Requests" and "My Donations"** are tabs on one page instead of two separate screens.
- **Admin charts** live on a dedicated staff-only `/dashboard/admin-stats/` page (Chart.js) rather
  than hacking Django's own admin templates — the real Django admin already handles all the
  Manage Users / Donors / Requests / CRUD from the spec, unmodified and fully reliable.
- **Donation eligibility** (~90-day gap between donations) is modeled as a real computed property
  (`Donor.is_eligible_to_donate`) and surfaced in the UI, not just a static field.

---

## 4. Environment Variables

See `.env.example` for the full list. Nothing is required for local development — every
setting has a safe fallback so `runserver` works immediately. Before deploying, at minimum set
`SECRET_KEY`, `DEBUG=False`, and `ALLOWED_HOSTS`.

---

## 5. Testing

```bash
python manage.py test
```

Runs 27 tests covering: custom user model + email login, registration, donor eligibility logic,
search filtering, permission checks (login-required, staff-only, ownership), the notification
signal, and the full accept → complete donation workflow (including the donation counter
increment). All were passing as of the last build.

---

## 6. Deployment Guide

This app ships production-ready defaults that activate automatically when `DEBUG=False`:
HSTS, secure cookies, SSL redirect, and WhiteNoise for compressed static file serving
(no separate nginx/S3 setup needed for static assets). It's also **Render-ready out of the
box** — see 6.1 below.

### 6.1 Deploying to Render

The project already includes everything Render's own Django guide asks for: `build.sh`,
`render.yaml`, a `.python-version` file, `dj-database-url` + `psycopg2-binary` in
`requirements.txt`, and `settings.py` auto-detects Render's `DATABASE_URL` and
`RENDER_EXTERNAL_HOSTNAME` — you don't need to edit any code.

**Step 1 — get the code onto GitHub** (Render deploys from a Git repo, not a zip):
```bash
cd bloodfinder
git init
git add .
git commit -m "Initial commit"
```
Then create an empty repository on GitHub and push:
```bash
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```

**Step 2 — deploy on Render (Blueprint method — recommended, one click):**
1. Go to the [Render Dashboard → Blueprints](https://dashboard.render.com/blueprints) → **New Blueprint Instance**
2. Connect the GitHub repo you just pushed
3. Render reads `render.yaml` automatically and sets up both the **web service** and a **free PostgreSQL database**, wires `DATABASE_URL` between them, and generates a random `SECRET_KEY` — all by itself
4. Before clicking Apply, open `render.yaml` and change `DJANGO_SUPERUSER_EMAIL` to your real email if you want an admin account created automatically (see below)
5. Click **Apply** — first deploy takes a few minutes

**Step 3 — log into the admin panel:**
Render's **free tier has no shell access**, so you can't run `createsuperuser` interactively.
`render.yaml` already handles this: it sets `DJANGO_SUPERUSER_PASSWORD` to `generateValue: true`,
and `build.sh` runs a custom `create_admin` command (safe to run on every deploy — it skips
if the account already exists) that creates that admin account automatically. After the first
deploy finishes, go to your web service's **Environment** tab on Render and copy the generated
value of `DJANGO_SUPERUSER_PASSWORD` — log in at `/admin/` with that + the email you set.

**Alternative — manual dashboard setup (no `render.yaml`):** create a Postgres database and a
Web Service separately in the dashboard, set **Build Command** to `bash build.sh` and **Start
Command** to `gunicorn bloodfinder.wsgi:application --workers 3`, then add `DATABASE_URL`
(from the database you created), `SECRET_KEY`, and `DEBUG=False` as environment variables.

> **Windows note:** if you unzip this project on Windows and then `git push`, `build.sh` often
> loses its "executable" flag in the process (Windows zip extraction doesn't preserve Unix
> permissions). Using `bash build.sh` as the build command — as `render.yaml` already does —
> sidesteps this entirely, since it doesn't rely on that flag at all.

### 6.2 Deploying elsewhere (any platform, general steps)

```bash
# 1. Set environment variables (see .env.example) — at minimum:
SECRET_KEY=<a long random string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com   # replace with your REAL domain — this is a placeholder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Collect static files (WhiteNoise serves these directly from Django)
python manage.py collectstatic --noinput

# 4. Run migrations
python manage.py migrate

# 5. Start with a real WSGI server (never runserver in production)
gunicorn bloodfinder.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

**This gets the Django app itself running correctly — it does not, by itself, make the
site reachable and secure on the internet.** What's still needed depends on where you deploy:

### 6.3 If you're on a PaaS (Render, Railway, Heroku, Fly.io)

You're basically done. These platforms terminate HTTPS and set `X-Forwarded-Proto` for you,
which this project already trusts correctly (see the `SECURE_PROXY_SSL_HEADER` note in
`settings.py`). Just:
- Set the required env vars in the platform's dashboard
- Set the start command to the `gunicorn` line above
- Add a release/build step running `python manage.py migrate && python manage.py collectstatic --noinput`
- The platform handles process supervision (restarts on crash/deploy) automatically

### 6.4 If you're on a raw VPS (DigitalOcean, EC2, Linode, a bare Ubuntu box)

The steps above are necessary but **not sufficient** — gunicorn on its own is not a public
web server and won't survive a reboot or a closed SSH session. You additionally need:

- **nginx (or similar) as a reverse proxy** in front of gunicorn, terminating HTTPS and
  forwarding to `127.0.0.1:8000` — this is also what makes `SECURE_SSL_REDIRECT` work correctly
  instead of causing a redirect loop (nginx must set `X-Forwarded-Proto`, which is standard
  in most nginx Django guides)
- **An SSL certificate** — Let's Encrypt via `certbot` is the usual free option
- **A process manager** (`systemd` service, or `supervisor`) so gunicorn restarts on crash and
  on server reboot, instead of dying when your terminal closes
- **DNS** pointing your domain at the server's IP

Without these, following just the steps above will either leave the site unreachable from a
real domain, or — if `DEBUG=False` is set without HTTPS actually in front of it — cause the
site to redirect-loop and appear broken, because `SECURE_SSL_REDIRECT` assumes HTTPS exists
somewhere in front of the app.

### 6.5 Switching from SQLite to PostgreSQL (manual platforms only — Render already does this)

`settings.py` already reads `DATABASE_URL` via `dj-database-url` and falls back to SQLite
when it isn't set. On any platform that gives you a Postgres connection string, just set
`DATABASE_URL` as an environment variable — no code change needed. If your platform doesn't
give you a ready-made `DATABASE_URL`, format one yourself:
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
```

### 6.6 Other things worth knowing before you call it done

- **Media uploads (profile pictures):** the default `FileSystemStorage` writes to local disk,
  which doesn't persist across deploys on most PaaS platforms (Render included, on its free
  tier). For real deployments, swap in an object storage backend (e.g. `django-storages` with
  S3/R2/Spaces) for `MEDIA` files.
- **Email:** set `EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend` and fill in
  `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — otherwise password reset and
  verification emails will keep printing to the console instead of actually sending.
- **Render's free tier spins down after inactivity** — the first request after a period of no
  traffic can take 30-60 seconds while it wakes back up. This is normal, not a bug.
- **Test with `DEBUG=False` locally first**, if you can — some template/static issues only
  surface once `DEBUG` is off.

### 6.7 Post-deploy checklist

- [ ] `SECRET_KEY` is a long random value, not the dev fallback
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` set correctly (handled automatically on Render; set manually elsewhere)
- [ ] HTTPS is actually terminated somewhere (PaaS platform, or nginx + certbot on a VPS)
- [ ] Real database configured (Postgres recommended for anything beyond a single worker)
- [ ] Real email backend configured (for password reset / verification to actually send)
- [ ] `collectstatic` run as part of the deploy step
- [ ] Process manager in place on a VPS (systemd/supervisor) so the app survives reboots/crashes
- [ ] Object storage configured for `/media/` if the platform's disk isn't persistent

---

## 7. API (DRF)

Read-only endpoints, ready to extend with auth/write support later:

- `GET /api/donors/` — paginated donor directory (filterable by `blood_group`, `division`, `is_available`)
- `GET /api/requests/` — paginated feed of open blood requests (filterable by `blood_group_needed`, `urgency`)

---

## 8. Tech Stack

**Backend:** Python 3.12+, Django 6.0, Django ORM, Django REST Framework, SQLite (dev)
**Frontend:** HTML5, CSS3 (custom, no build step), Bootstrap 5.3 (CDN), vanilla JavaScript, Bootstrap Icons, Chart.js (admin stats only), Google Fonts (Poppins)
**Auth:** Django's built-in auth system with a custom `User` model
**Deployment-ready:** WhiteNoise, gunicorn, environment-based configuration via `python-dotenv`
