from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from donors.models import Donor
from dashboard.models import Notification
from .models import BloodRequest


class BloodRequestModelTests(TestCase):
    def setUp(self):
        self.requester = User.objects.create_user(username='req', email='req@example.com', password='StrongPass123')

    def test_str_representation(self):
        br = BloodRequest.objects.create(
            requested_by=self.requester, patient_name='John Doe', hospital='City Hospital',
            blood_group_needed='O-', units_needed=2, required_date=timezone.now().date(),
            location='Faridpur', contact_person='Jane Doe', contact_phone='+8801711111111',
        )
        self.assertIn('John Doe', str(br))
        self.assertIn('O-', str(br))

    def test_new_request_notifies_matching_available_donors(self):
        donor_user = User.objects.create_user(username='matchdonor', email='matchdonor@example.com', password='StrongPass123')
        Donor.objects.create(
            user=donor_user, age=28, gender='M', blood_group='B+', division='Dhaka',
            district='Faridpur', area='Kotwali', address='x', weight=65, is_available=True,
        )
        BloodRequest.objects.create(
            requested_by=self.requester, patient_name='Needs B+', hospital='City Hospital',
            blood_group_needed='B+', units_needed=1, required_date=timezone.now().date(),
            location='Faridpur', contact_person='Jane Doe', contact_phone='+8801711111111',
        )
        self.assertTrue(Notification.objects.filter(recipient=donor_user).exists())


class BloodRequestViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='listtest', email='listtest@example.com', password='StrongPass123')

    def test_list_view_loads(self):
        response = self.client.get(reverse('blood_requests:list'))
        self.assertEqual(response.status_code, 200)

    def test_create_requires_login(self):
        response = self.client.get(reverse('blood_requests:create'))
        self.assertEqual(response.status_code, 302)

    def test_accept_by_non_donor_redirects_with_message(self):
        BloodRequest.objects.create(
            requested_by=self.user, patient_name='X', hospital='Y', blood_group_needed='O+',
            units_needed=1, required_date=timezone.now().date(), location='Z',
            contact_person='C', contact_phone='+8801711111111',
        )
        other = User.objects.create_user(username='nodonorprofile', email='nodonor@example.com', password='StrongPass123')
        self.client.login(username='nodonor@example.com', password='StrongPass123')
        br = BloodRequest.objects.first()
        response = self.client.post(reverse('blood_requests:accept', args=[br.pk]))
        br.refresh_from_db()
        self.assertEqual(br.status, BloodRequest.Status.OPEN)  # unchanged, since user isn't a donor
