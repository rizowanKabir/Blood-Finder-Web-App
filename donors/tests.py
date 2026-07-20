from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .models import Donor


class DonorModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='don', email='don@example.com', password='StrongPass123')

    def test_eligible_when_no_last_donation(self):
        donor = Donor.objects.create(
            user=self.user, age=25, gender='M', blood_group='O+', division='Dhaka',
            district='Faridpur', area='Kotwali', address='x', weight=60,
        )
        self.assertTrue(donor.is_eligible_to_donate)

    def test_not_eligible_within_90_days(self):
        donor = Donor.objects.create(
            user=self.user, age=25, gender='M', blood_group='O+', division='Dhaka',
            district='Faridpur', area='Kotwali', address='x', weight=60,
            last_donation_date=timezone.now().date() - timedelta(days=10),
        )
        self.assertFalse(donor.is_eligible_to_donate)
        self.assertGreater(donor.days_until_eligible, 0)


class DonorViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='don2', email='don2@example.com', password='StrongPass123')
        Donor.objects.create(
            user=self.user, age=30, gender='F', blood_group='A+', division='Dhaka',
            district='Faridpur', area='Kotwali', address='x', weight=55, is_available=True,
        )

    def test_donor_list_loads(self):
        response = self.client.get(reverse('donors:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A+')

    def test_donor_list_filters_by_blood_group(self):
        response = self.client.get(reverse('donors:list'), {'blood_group': 'O-'})
        self.assertNotContains(response, 'Kotwali')

    def test_become_donor_requires_login(self):
        response = self.client.get(reverse('donors:create'))
        self.assertEqual(response.status_code, 302)
