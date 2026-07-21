"""
Django settings for the Blood Finder project.
Senior-dev note: all secrets/environment-specific values are read from
environment variables (via a .env file in development) with safe dev
fallbacks, so `manage.py runserver` works out of the box, and production
just needs a real .env / platform env vars. See .env.example + README.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'dev-only-insecure-secret-key-change-me-before-deploying-3f9a7c2e1b'
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()
]

# Render sets this automatically for every web service — trust it so the
# site works on its *.onrender.com URL without you needing to know that
# URL in advance and add it to ALLOWED_HOSTS by hand.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'rest_framework',

    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'donors.apps.DonorsConfig',
    'blood_requests.apps.BloodRequestsConfig',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bloodfinder.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.notifications_processor',
                'core.context_processors.site_stats_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'bloodfinder.wsgi.application'
ASGI_APPLICATION = 'bloodfinder.asgi.application'

# ---------------------------------------------------------------------------
# Database (SQLite for development; swap DATABASE_URL-style envs for prod)
# ---------------------------------------------------------------------------
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        # Falls back to local SQLite when DATABASE_URL isn't set (i.e. on
        # your own machine). Render sets DATABASE_URL automatically once
        # you attach a Render PostgreSQL database to this web service —
        # no code change needed to switch between the two.
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'accounts:login'
AUTHENTICATION_BACKENDS = ['accounts.backends.CaseInsensitiveEmailBackend'] 
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Dhaka')
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG else
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

MAX_UPLOAD_SIZE_MB = 2

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Messages -> map Django's "error" tag to Bootstrap's "danger" class
# ---------------------------------------------------------------------------
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

# ---------------------------------------------------------------------------
# Email (console backend in dev; real SMTP in prod via env vars)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Blood Finder <noreply@bloodfinder.example>')

SITE_NAME = 'Blood Finder'
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'localhost:8000')
SITE_PROTOCOL = os.environ.get('SITE_PROTOCOL', 'http')

# ---------------------------------------------------------------------------
# Django REST Framework (read-only public API surface)
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'anon': '60/minute'},
}

# ---------------------------------------------------------------------------
# Security hardening (auto-tightens when DEBUG=False)
# ---------------------------------------------------------------------------
if not DEBUG:
    # If you're behind a reverse proxy or platform load balancer that
    # terminates HTTPS (nginx, Railway, Render, Heroku, Fly.io, an AWS
    # ALB, Cloudflare...) Django itself only ever sees plain HTTP from
    # that proxy. Without telling it which header to trust, it thinks
    # every request is insecure and SECURE_SSL_REDIRECT below causes an
    # infinite redirect loop. This is safe ONLY because real proxies set
    # (and strip any client-supplied copy of) this header themselves —
    # never enable it if gunicorn is exposed directly to the internet
    # with no proxy in front, since then a client could forge it.
    if os.environ.get('USE_X_FORWARDED_PROTO', 'True') == 'True':
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

