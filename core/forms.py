from django import forms

from .models import ContactMessage

INPUT = 'form-control custom-input'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'you@example.com'}),
            'subject': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': INPUT, 'rows': 5, 'placeholder': 'How can we help?'}),
        }
