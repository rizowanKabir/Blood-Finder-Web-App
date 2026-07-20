from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from accounts.models import phone_validator
from core.constants import BLOOD_GROUP_CHOICES


class BloodRequest(models.Model):
    class Urgency(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        URGENT = 'urgent', 'Urgent'
        EMERGENCY = 'emergency', 'Emergency'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        ACCEPTED = 'accepted', 'Accepted'
        COMPLETED = 'completed', 'Completed'

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='blood_requests', verbose_name='Requested By'
    )
    patient_name = models.CharField(max_length=150, verbose_name='Patient Name')
    hospital = models.CharField(max_length=200, verbose_name='Hospital')
    blood_group_needed = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES,
                                           verbose_name='Blood Group Needed', db_index=True)
    units_needed = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)], verbose_name='Units Needed'
    )
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.NORMAL,
                                verbose_name='Urgency', db_index=True)
    required_date = models.DateField(verbose_name='Required Date')
    location = models.CharField(max_length=200, verbose_name='Location')
    contact_person = models.CharField(max_length=150, verbose_name='Contact Person')
    contact_phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name='Contact Phone')
    description = models.TextField(blank=True, verbose_name='Additional Details')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN,
                               verbose_name='Status', db_index=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='accepted_requests', verbose_name='Accepted By'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blood Request'
        verbose_name_plural = 'Blood Requests'
        indexes = [models.Index(fields=['blood_group_needed', 'status', 'urgency'])]

    def __str__(self):
        return f"{self.patient_name} needs {self.blood_group_needed} at {self.hospital}"

    def get_absolute_url(self):
        return reverse('blood_requests:detail', args=[self.pk])

    @property
    def urgency_badge_class(self):
        return {'normal': 'bg-secondary', 'urgent': 'bg-warning text-dark', 'emergency': 'bg-danger'}.get(self.urgency, 'bg-secondary')

    @property
    def status_badge_class(self):
        return {'open': 'bg-success', 'accepted': 'bg-info text-dark', 'completed': 'bg-secondary'}.get(self.status, 'bg-secondary')
