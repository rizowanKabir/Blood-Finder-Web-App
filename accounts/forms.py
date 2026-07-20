from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User

TEXT_INPUT_CLASS = 'form-control custom-input'
SELECT_CLASS = 'form-select custom-input'
CHECK_CLASS = 'form-check-input'


class RegisterForm(UserCreationForm):
    """Registration form. Donor-specific fields live in donors.forms.DonorForm,
    kept as a separate step ("Become a Donor") so signing up stays fast."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'you@example.com'})
    )
    first_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'Last name'})
    )
    phone_number = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': '+8801XXXXXXXXX'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': TEXT_INPUT_CLASS, 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': TEXT_INPUT_CLASS, 'placeholder': 'Confirm password'})

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': TEXT_INPUT_CLASS, 'placeholder': 'you@example.com', 'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'class': TEXT_INPUT_CLASS, 'placeholder': 'Password'
        })


class ProfileEditForm(forms.ModelForm):
    """Base-account fields only — donor-specific fields are edited via donors.forms.DonorForm."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS}),
            'phone_number': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS}),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'image-input-trigger d-none', 'accept': 'image/*', 'data-preview-target': 'imagePreview',
            }),
        }
