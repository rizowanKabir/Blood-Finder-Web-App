from django.apps import AppConfig


class BloodRequestsConfig(AppConfig):
    name = 'blood_requests'
    verbose_name = 'Blood Requests'

    def ready(self):
        from . import signals  # noqa: F401 — connects the post_save receiver
