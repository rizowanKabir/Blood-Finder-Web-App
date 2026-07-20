from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Notification


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dashuser', email='dashuser@example.com', password='StrongPass123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_when_logged_in(self):
        self.client.login(username='dashuser@example.com', password='StrongPass123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_admin_stats_forbidden_for_non_staff(self):
        self.client.login(username='dashuser@example.com', password='StrongPass123')
        response = self.client.get(reverse('dashboard:admin_stats'))
        self.assertEqual(response.status_code, 403)

    def test_notifications_page_marks_unread_as_read(self):
        Notification.objects.create(recipient=self.user, title='Hi', message='Test message')
        self.client.login(username='dashuser@example.com', password='StrongPass123')
        self.client.get(reverse('dashboard:notifications'))
        self.assertTrue(Notification.objects.get(recipient=self.user).is_read)
