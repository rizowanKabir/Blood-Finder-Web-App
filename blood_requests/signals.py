from django.db.models.signals import post_save
from django.dispatch import receiver

from donors.models import Donor
from .models import BloodRequest


@receiver(post_save, sender=BloodRequest)
def notify_matching_donors_on_new_request(sender, instance, created, **kwargs):
    """When a new blood request comes in, alert available donors with a
    matching blood group so they see it on their dashboard bell icon."""
    if not created:
        return
    # local import: avoids any cross-app import-order issues at startup
    from dashboard.models import Notification

    matching_donors = (
        Donor.objects
        .filter(blood_group=instance.blood_group_needed, is_available=True)
        .exclude(user_id=instance.requested_by_id)
        .select_related('user')[:100]
    )
    Notification.objects.bulk_create([
        Notification(
            recipient=donor.user,
            title=f'{instance.blood_group_needed} blood needed — {instance.urgency.title()}',
            message=f'{instance.patient_name} needs {instance.units_needed} unit(s) of '
                     f'{instance.blood_group_needed} at {instance.hospital} ({instance.location}).',
            link=instance.get_absolute_url(),
        )
        for donor in matching_donors
    ])
