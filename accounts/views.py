from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView

from .forms import RegisterForm, StyledAuthenticationForm
from .models import User
from .tokens import email_verification_token


def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    link = request.build_absolute_uri(reverse_lazy('accounts:verify_email', kwargs={'uidb64': uid, 'token': token}))
    subject = 'Verify your Blood Finder account'
    message = render_to_string('emails/verification_email.txt', {'user': user, 'link': link})
    send_mail(subject, message, None, [user.email], fail_silently=True)


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        _send_verification_email(self.request, self.object)
        messages.success(
            self.request,
            f'Welcome, {self.object.first_name}! Your account is ready. '
            'We\'ve sent a verification link to your email.'
        )
        return response


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You\'ve been logged out. See you soon!')
        return super().dispatch(request, *args, **kwargs)


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return render(request, 'accounts/verify_email_result.html', {'success': True})
    return render(request, 'accounts/verify_email_result.html', {'success': False})


def resend_verification_email(request):
    if request.user.is_authenticated and not request.user.is_email_verified:
        _send_verification_email(request, request.user)
        messages.success(request, 'Verification email sent again — check your inbox.')
    return redirect('dashboard:home')


# ---------------------------------------------------------------------------
# Password reset — thin wrappers around Django's built-in views, just to
# point at our own styled templates and keep everything namespaced under
# accounts:.
# ---------------------------------------------------------------------------
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'emails/password_reset_email.txt'
    subject_template_name = 'emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    token_generator = default_token_generator


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
