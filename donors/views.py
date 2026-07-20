from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import DonorForm, DonorSearchForm
from .models import Donor


class DonorListView(ListView):
    model = Donor
    template_name = 'donors/donor_list.html'
    context_object_name = 'donors'
    paginate_by = 9

    def get_queryset(self):
        qs = Donor.objects.select_related('user').all()
        form = DonorSearchForm(self.request.GET or None)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('blood_group'):
                qs = qs.filter(blood_group=data['blood_group'])
            if data.get('division'):
                qs = qs.filter(division=data['division'])
            if data.get('district'):
                qs = qs.filter(district__icontains=data['district'])
            if data.get('area'):
                qs = qs.filter(area__icontains=data['area'])
            if data.get('available_only'):
                qs = qs.filter(is_available=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = DonorSearchForm(self.request.GET or None)
        ctx['result_count'] = ctx['paginator'].count
        # preserve filters across pagination links
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['querystring'] = params.urlencode()
        return ctx


class DonorDetailView(DetailView):
    model = Donor
    template_name = 'donors/donor_detail.html'
    context_object_name = 'donor'


class DonorCreateView(LoginRequiredMixin, CreateView):
    model = Donor
    form_class = DonorForm
    template_name = 'donors/donor_form.html'
    success_url = reverse_lazy('dashboard:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'donor_profile'):
            messages.info(request, 'You already have a donor profile — you can edit it below.')
            return redirect('donors:edit', pk=request.user.donor_profile.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        self.request.user.user_type = 'donor'
        self.request.user.save(update_fields=['user_type'])
        messages.success(self.request, 'You are now a registered blood donor. Thank you!')
        return response


class DonorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Donor
    form_class = DonorForm
    template_name = 'donors/donor_form.html'
    success_url = reverse_lazy('dashboard:home')

    def test_func(self):
        return self.get_object().user_id == self.request.user.id

    def form_valid(self, form):
        messages.success(self.request, 'Your donor profile has been updated.')
        return super().form_valid(form)


class DonorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Donor
    template_name = 'includes/confirm_delete.html'
    success_url = reverse_lazy('dashboard:home')

    def test_func(self):
        return self.get_object().user_id == self.request.user.id

    def form_valid(self, form):
        messages.success(self.request, 'Your donor profile has been removed.')
        return super().form_valid(form)


@require_POST
def toggle_availability(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    if donor.user_id != request.user.id:
        messages.error(request, 'You can only update your own availability.')
        return redirect('donors:detail', pk=pk)
    donor.is_available = not donor.is_available
    donor.save(update_fields=['is_available'])
    messages.success(request, f'You are now marked as {"available" if donor.is_available else "unavailable"}.')
    return redirect('dashboard:home')


def quick_search_api(request):
    """Lightweight JSON endpoint behind the homepage's instant search widget."""
    form = DonorSearchForm(request.GET or None)
    qs = Donor.objects.select_related('user').filter(is_available=True)
    if form.is_valid():
        data = form.cleaned_data
        if data.get('blood_group'):
            qs = qs.filter(blood_group=data['blood_group'])
        if data.get('division'):
            qs = qs.filter(division=data['division'])
        if data.get('district'):
            qs = qs.filter(district__icontains=data['district'])
    total = qs.count()
    preview = [
        {
            'name': d.get_full_name(),
            'blood_group': d.blood_group,
            'district': d.district,
            'division': d.division,
            'url': d.get_absolute_url(),
        }
        for d in qs[:5]
    ]
    return JsonResponse({'total': total, 'results': preview})
