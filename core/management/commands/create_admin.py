import os

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Create or update a superuser from DJANGO_SUPERUSER_* environment variables."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not all([email, username, password]):
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_EMAIL/_USERNAME/_PASSWORD not all set. Skipping."
                )
            )
            return

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
            },
        )

        user.username = username
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{email}' created successfully.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{email}' updated successfully.")
            )

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
