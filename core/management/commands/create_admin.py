import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    """
    Creates a superuser from DJANGO_SUPERUSER_EMAIL / _USERNAME / _PASSWORD
    env vars, but only if one doesn't already exist for that email — safe
    to call on every single deploy (e.g. from build.sh), unlike Django's
    own `createsuperuser --noinput`, which errors out on the 2nd deploy.

    Prints diagnostics (never the password itself) on every run, since
    hosts like Render's free tier give no shell access to inspect the
    database directly — the deploy log is the only visibility available.

    If an account with that email already exists but you need to repair
    its password/staff status, set DJANGO_SUPERUSER_FORCE_RESET=True and
    redeploy. Turn it back off afterwards, or every future deploy will
    keep resetting the password back to whatever DJANGO_SUPERUSER_PASSWORD
    currently holds.
    """
    help = "Idempotently creates a superuser from DJANGO_SUPERUSER_* env vars. DJANGO_SUPERUSER_FORCE_RESET=True repairs an existing account instead of skipping it."

    def handle(self, *args, **options):
        raw_email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        force_reset = os.environ.get('DJANGO_SUPERUSER_FORCE_RESET', 'False') == 'True'

        self.stdout.write(f'[create_admin] DJANGO_SUPERUSER_EMAIL={raw_email!r}')
        self.stdout.write(f'[create_admin] DJANGO_SUPERUSER_USERNAME={username!r}')
        self.stdout.write(f'[create_admin] DJANGO_SUPERUSER_PASSWORD length={len(password) if password else 0}')

        if not all([raw_email, username, password]):
            self.stdout.write(
                'DJANGO_SUPERUSER_EMAIL/_USERNAME/_PASSWORD not all set — skipping superuser creation. '
                'Double-check the exact key names in the Environment tab for typos.'
            )
            return

        # Emails are matched case-insensitively everywhere in this app
        # (see accounts/backends.py) — normalize here too, so what's
        # stored always matches what login will look up.
        email = raw_email.strip().lower()

        existing = User.objects.filter(email__iexact=email).first()
        if existing:
            self.stdout.write(
                f'[create_admin] existing account found -> stored email={existing.email!r}, '
                f'is_staff={existing.is_staff}, is_superuser={existing.is_superuser}, is_active={existing.is_active}'
            )
            if force_reset:
                existing.email = email
                existing.username = username
                existing.set_password(password)
                existing.is_staff = True
                existing.is_superuser = True
                existing.is_active = True
                existing.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Superuser {email} already existed — password/permissions reset '
                    f'because DJANGO_SUPERUSER_FORCE_RESET=True.'
                ))
            else:
                self.stdout.write(
                    f'Superuser with email {email} already exists — skipping '
                    f'(set DJANGO_SUPERUSER_FORCE_RESET=True to reset its password instead).'
                )
            return

        User.objects.create_superuser(email=email, username=username, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser {email} created.'))

# import os

# from django.core.management.base import BaseCommand

# from accounts.models import User


# class Command(BaseCommand):
#     """
#     Creates a superuser from DJANGO_SUPERUSER_EMAIL / _USERNAME / _PASSWORD
#     env vars, but only if one doesn't already exist for that email — safe
#     to call on every single deploy (e.g. from build.sh), unlike Django's
#     own `createsuperuser --noinput`, which errors out on the 2nd deploy.

#     Exists mainly for hosts like Render's free tier, which don't give you
#     shell access to run `createsuperuser` interactively after deploy.
#     """
#     help = "Idempotently creates a superuser from DJANGO_SUPERUSER_* env vars, if one doesn't already exist."

#     def handle(self, *args, **options):
#         email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
#         username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
#         password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

#         if not all([email, username, password]):
#             self.stdout.write('DJANGO_SUPERUSER_EMAIL/_USERNAME/_PASSWORD not all set — skipping superuser creation.')
#             return

#         if User.objects.filter(email=email).exists():
#             self.stdout.write(f'Superuser with email {email} already exists — skipping.')
#             return

#         User.objects.create_superuser(email=email, username=username, password=password)
#         self.stdout.write(self.style.SUCCESS(f'Superuser {email} created.'))
