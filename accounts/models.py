from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models
from django.urls import reverse

from core.constants import USER_TYPE_CHOICES

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message='Enter a valid phone number (7-15 digits, optional leading +).'
)


class User(AbstractUser):
    """
    Custom user model, extending Django's AbstractUser so we keep
    is_staff/is_superuser/permissions/groups for free, while logging
    in with email (more natural for a public-facing app) instead of
    a separate username. `username` is kept as a required, unique
    handle (shown in the UI) rather than removed outright, to avoid
    the extra churn of a fully custom manager.
    """
    email = models.EmailField('email address', unique=True)
    phone_number = models.CharField(
        max_length=20, validators=[phone_validator], blank=True,
        verbose_name='Phone Number'
    )
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default='user',
        verbose_name='User Type'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/%Y/%m/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='Profile Picture'
    )
    is_email_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_absolute_url(self):
        return reverse('dashboard:home')

    @property
    def is_donor(self):
        return hasattr(self, 'donor_profile')

    def profile_completion_percentage(self):
        """Used by the dashboard progress bar."""
        fields_to_check = [self.first_name, self.last_name, self.phone_number, self.profile_picture]
        filled = sum(1 for f in fields_to_check if f)
        total = len(fields_to_check) + 1  # +1 for "has a donor profile" below
        if self.is_donor:
            filled += 1
            donor = self.donor_profile
            donor_fields = [
                donor.division, donor.district, donor.area, donor.address,
                donor.weight, donor.blood_group,
            ]
            filled += sum(1 for f in donor_fields if f)
            total += len(donor_fields)
        return round((filled / total) * 100)
