from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView, UpdateView

from accounts.forms import ProfileEditForm
from blood_requests.models import BloodRequest
from donors.models import Donor
from .models import Notification


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard_home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['profile_completion'] = user.profile_completion_percentage()
        ctx['donor_profile'] = getattr(user, 'donor_profile', None)
        ctx['my_requests_count'] = user.blood_requests.count()
        ctx['my_open_requests_count'] = user.blood_requests.filter(status=BloodRequest.Status.OPEN).count()
        ctx['my_donations_count'] = BloodRequest.objects.filter(accepted_by=user, status=BloodRequest.Status.COMPLETED).count()
        ctx['recent_notifications'] = user.notifications.all()[:5]
        return ctx


class MyActivityView(LoginRequiredMixin, TemplateView):
    """Combines 'My Requests' and 'My Donations' as tabs on one page —
    avoids two near-identical list pages for what's really one section."""
    template_name = 'dashboard/my_activity.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['my_requests'] = self.request.user.blood_requests.all()
        ctx['my_donations'] = BloodRequest.objects.filter(accepted_by=self.request.user).select_related('requested_by')
        return ctx


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 15

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return response


@require_POST
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect(notification.get_absolute_url())


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = 'dashboard/edit_profile.html'
    success_url = reverse_lazy('dashboard:home')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated.')
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'dashboard/change_password.html'
    success_url = reverse_lazy('dashboard:home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control custom-input'
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed.')
        return super().form_valid(form)


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Staff-only stats dashboard — sits alongside (not instead of) the
    real Django admin, which already handles the manage-everything CRUD."""
    template_name = 'dashboard/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_donors'] = Donor.objects.count()
        ctx['available_donors'] = Donor.objects.filter(is_available=True).count()
        ctx['total_requests'] = BloodRequest.objects.count()
        ctx['open_requests'] = BloodRequest.objects.filter(status=BloodRequest.Status.OPEN).count()
        ctx['cities_covered'] = Donor.objects.values('district').distinct().count()
        ctx['total_users'] = self.request.user.__class__.objects.count()
        return ctx


def admin_stats_api(request):
    """JSON feed consumed by Chart.js on the admin dashboard template."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)

    donors_by_group = list(
        Donor.objects.values('blood_group').annotate(count=Count('id')).order_by('blood_group')
    )
    requests_by_status = list(
        BloodRequest.objects.values('status').annotate(count=Count('id')).order_by('status')
    )
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    requests_by_month = list(
        BloodRequest.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    return JsonResponse({
        'donors_by_group': donors_by_group,
        'requests_by_status': requests_by_status,
        'requests_by_month': [
            {'month': r['month'].strftime('%b %Y'), 'count': r['count']} for r in requests_by_month
        ],
    })
