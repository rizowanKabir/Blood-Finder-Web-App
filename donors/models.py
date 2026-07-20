from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.constants import (
    BLOOD_GROUP_CHOICES, GENDER_CHOICES, DIVISION_CHOICES,
    MIN_DONOR_AGE, MAX_DONOR_AGE, MIN_DONOR_WEIGHT_KG, DONATION_ELIGIBILITY_GAP_DAYS,
)


class Donor(models.Model):
    """Extended donor profile. One-to-one with User — a user "becomes a
    donor" by filling this out, rather than it existing for everyone."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='donor_profile', verbose_name='User Account'
    )
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_DONOR_AGE), MaxValueValidator(MAX_DONOR_AGE)],
        verbose_name='Age', help_text=f'Must be between {MIN_DONOR_AGE} and {MAX_DONOR_AGE}'
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Gender')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, verbose_name='Blood Group', db_index=True)
    division = models.CharField(max_length=50, choices=DIVISION_CHOICES, verbose_name='Division', db_index=True)
    district = models.CharField(max_length=100, verbose_name='District', db_index=True)
    area = models.CharField(max_length=100, verbose_name='Area')
    address = models.TextField(verbose_name='Full Address')
    last_donation_date = models.DateField(null=True, blank=True, verbose_name='Last Donation Date')
    is_available = models.BooleanField(default=True, verbose_name='Available for Donation', db_index=True)
    is_featured = models.BooleanField(default=False, verbose_name='Featured Donor')
    medical_notes = models.TextField(blank=True, verbose_name='Medical Notes',
                                      help_text='Conditions/medications relevant to donation eligibility')
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal(str(MIN_DONOR_WEIGHT_KG)))],
        verbose_name='Weight (kg)'
    )
    occupation = models.CharField(max_length=100, blank=True, verbose_name='Occupation')
    total_donations = models.PositiveIntegerField(default=0, verbose_name='Total Donations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Donor'
        verbose_name_plural = 'Donors'
        indexes = [models.Index(fields=['blood_group', 'division', 'is_available'])]

    def __str__(self):
        return f"{self.get_full_name()} ({self.blood_group})"

    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

    def get_absolute_url(self):
        return reverse('donors:detail', args=[self.pk])

    @property
    def is_eligible_to_donate(self):
        """Standard ~3 month gap rule between whole-blood donations."""
        if not self.last_donation_date:
            return True
        return (timezone.now().date() - self.last_donation_date).days >= DONATION_ELIGIBILITY_GAP_DAYS

    @property
    def days_until_eligible(self):
        if self.is_eligible_to_donate:
            return 0
        next_date = self.last_donation_date + timedelta(days=DONATION_ELIGIBILITY_GAP_DAYS)
        return (next_date - timezone.now().date()).days
