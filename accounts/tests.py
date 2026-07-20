from django.test import TestCase, Client
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', email='alice@example.com', password='StrongPass123',
            first_name='Alice', last_name='Nguyen',
        )

    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_login_with_email(self):
        self.assertTrue(self.client.login(username='alice@example.com', password='StrongPass123'))

    def test_str_returns_full_name(self):
        self.assertEqual(str(self.user), 'Alice Nguyen')

    def test_profile_completion_partial(self):
        pct = self.user.profile_completion_percentage()
        self.assertGreater(pct, 0)
        self.assertLess(pct, 100)


class AuthViewTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'bob', 'first_name': 'Bob', 'last_name': 'Lee',
            'email': 'bob@example.com', 'phone_number': '+8801711111111',
            'password1': 'AnotherStrongPass1', 'password2': 'AnotherStrongPass1',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='bob@example.com').exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_requires_post(self):
        User.objects.create_user(username='carol', email='carol@example.com', password='StrongPass123')
        self.client.login(username='carol@example.com', password='StrongPass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 405)  # GET not allowed on Django 5+ LogoutView
