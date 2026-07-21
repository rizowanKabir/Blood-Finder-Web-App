#!/usr/bin/env bash
# Render runs this on every deploy. Exit on first error so a broken
# build never gets marked "live".
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# Safe to run every time — creates the admin account only if it doesn't
# exist yet. Only does anything if DJANGO_SUPERUSER_* env vars are set.
python manage.py create_admin

