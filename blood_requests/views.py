from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import BloodRequestForm, BloodRequestFilterForm
from .models import BloodRequest


class BloodRequestListView(ListView):
    model = BloodRequest
    template_name = 'blood_requests/request_list.html'
    context_object_name = 'requests'
    paginate_by = 8

    def get_queryset(self):
        qs = BloodRequest.objects.select_related('requested_by').all()
        form = BloodRequestFilterForm(self.request.GET or None)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('blood_group_needed'):
                qs = qs.filter(blood_group_needed=data['blood_group_needed'])
            if data.get('urgency'):
                qs = qs.filter(urgency=data['urgency'])
            if data.get('status'):
                qs = qs.filter(status=data['status'])
            elif not self.request.GET:
                qs = qs.filter(status=BloodRequest.Status.OPEN)
        else:
            qs = qs.filter(status=BloodRequest.Status.OPEN)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = BloodRequestFilterForm(self.request.GET or None)
        ctx['result_count'] = ctx['paginator'].count
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['querystring'] = params.urlencode()
        return ctx


class BloodRequestDetailView(DetailView):
    model = BloodRequest
    template_name = 'blood_requests/request_detail.html'
    context_object_name = 'blood_request'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        obj = self.object
        ctx['can_manage'] = user.is_authenticated and (user.id == obj.requested_by_id or user.is_staff)
        ctx['can_complete'] = user.is_authenticated and (
            user.id == obj.requested_by_id or user.id == obj.accepted_by_id or user.is_staff
        )
        return ctx


class BloodRequestCreateView(LoginRequiredMixin, CreateView):
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = 'blood_requests/request_form.html'

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        messages.success(self.request, 'Your blood request has been posted. Nearby donors have been notified.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class BloodRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = 'blood_requests/request_form.html'

    def test_func(self):
        obj = self.get_object()
        return obj.requested_by_id == self.request.user.id or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Blood request updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class BloodRequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BloodRequest
    template_name = 'includes/confirm_delete.html'
    success_url = reverse_lazy('blood_requests:list')

    def test_func(self):
        obj = self.get_object()
        return obj.requested_by_id == self.request.user.id or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Blood request removed.')
        return super().form_valid(form)


@require_POST
def accept_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if not hasattr(request.user, 'donor_profile'):
        messages.error(request, 'Only registered donors can accept requests. Become a donor first.')
        return redirect('donors:create')
    if blood_request.status != BloodRequest.Status.OPEN:
        messages.warning(request, 'This request is no longer open.')
        return redirect(blood_request.get_absolute_url())

    blood_request.status = BloodRequest.Status.ACCEPTED
    blood_request.accepted_by = request.user
    blood_request.save(update_fields=['status', 'accepted_by', 'updated_at'])

    from dashboard.models import Notification
    Notification.objects.create(
        recipient=blood_request.requested_by,
        title='A donor accepted your request',
        message=f'{request.user.get_full_name() or request.user.username} has offered to donate '
                 f'{blood_request.blood_group_needed} for {blood_request.patient_name}.',
        link=blood_request.get_absolute_url(),
    )
    messages.success(request, 'Thank you! You have accepted this request — please coordinate with the contact person.')
    return redirect(blood_request.get_absolute_url())


@require_POST
def complete_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    allowed = request.user.id in {blood_request.requested_by_id, blood_request.accepted_by_id} or request.user.is_staff
    if not allowed:
        messages.error(request, 'Only the requester, accepting donor, or an admin can mark this complete.')
        return redirect(blood_request.get_absolute_url())

    blood_request.status = BloodRequest.Status.COMPLETED
    blood_request.save(update_fields=['status', 'updated_at'])

    if blood_request.accepted_by_id and hasattr(blood_request.accepted_by, 'donor_profile'):
        donor = blood_request.accepted_by.donor_profile
        donor.total_donations += 1
        donor.last_donation_date = blood_request.updated_at.date()
        donor.save(update_fields=['total_donations', 'last_donation_date'])

    messages.success(request, 'Marked as completed. Thank you for helping save a life!')
    return redirect(blood_request.get_absolute_url())
