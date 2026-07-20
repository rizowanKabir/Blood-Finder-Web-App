from django.test import TestCase
from django.urls import reverse

from .models import FAQ, Testimonial


class CorePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_loads(self):
        self.assertEqual(self.client.get(reverse('core:about')).status_code, 200)

    def test_privacy_page_loads(self):
        self.assertEqual(self.client.get(reverse('core:privacy')).status_code, 200)

    def test_terms_page_loads(self):
        self.assertEqual(self.client.get(reverse('core:terms')).status_code, 200)

    def test_contact_form_submission(self):
        response = self.client.post(reverse('core:contact'), {
            'name': 'Test User', 'email': 'test@example.com',
            'subject': 'Hello', 'message': 'Just testing the contact form.',
        })
        self.assertEqual(response.status_code, 302)

    def test_home_shows_active_faq_only(self):
        FAQ.objects.create(question='Visible?', answer='Yes', is_active=True)
        FAQ.objects.create(question='Hidden?', answer='No', is_active=False)
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Visible?')
        self.assertNotContains(response, 'Hidden?')
