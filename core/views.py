from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from donors.models import Donor
from blood_requests.models import BloodRequest
from core.constants import BLOOD_GROUP_CHOICES, DIVISION_CHOICES
from .forms import ContactForm
from .models import Testimonial, FAQ


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['available_donors_count'] = Donor.objects.filter(is_available=True).count()
        ctx['total_requests_count'] = BloodRequest.objects.count()
        ctx['cities_covered_count'] = Donor.objects.values('district').distinct().count()
        ctx['total_donors_count'] = Donor.objects.count()
        ctx['donor_blood_groups'] = BLOOD_GROUP_CHOICES
        ctx['donor_divisions'] = DIVISION_CHOICES
        # One combined showcase (featured first, then most recent) rather
        # than two near-identical "featured" / "recently joined" grids.
        ctx['showcase_donors'] = Donor.objects.select_related('user').filter(is_available=True)[:8]
        ctx['testimonials'] = Testimonial.objects.filter(is_active=True)[:6]
        ctx['faqs'] = FAQ.objects.filter(is_active=True)
        ctx['urgent_requests'] = BloodRequest.objects.filter(
            status=BloodRequest.Status.OPEN, urgency__in=['urgent', 'emergency']
        ).select_related('requested_by')[:4]
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    template_name = 'core/terms.html'


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks for reaching out — we'll get back to you soon.")
        return super().form_valid(form)
