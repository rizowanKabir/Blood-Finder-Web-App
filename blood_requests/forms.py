from django import forms

from .models import BloodRequest

INPUT = 'form-control custom-input'
SELECT = 'form-select custom-input'


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'patient_name', 'hospital', 'blood_group_needed', 'units_needed', 'urgency',
            'required_date', 'location', 'contact_person', 'contact_phone', 'description',
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Patient full name'}),
            'hospital': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Hospital / clinic name'}),
            'blood_group_needed': forms.Select(attrs={'class': SELECT}),
            'units_needed': forms.NumberInput(attrs={'class': INPUT, 'min': 1, 'max': 20}),
            'urgency': forms.Select(attrs={'class': SELECT}),
            'required_date': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'City / area'}),
            'contact_person': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Contact person name'}),
            'contact_phone': forms.TextInput(attrs={'class': INPUT, 'placeholder': '+8801XXXXXXXXX'}),
            'description': forms.Textarea(attrs={'class': INPUT, 'rows': 4, 'placeholder': 'Any additional details (optional)'}),
        }


class BloodRequestFilterForm(forms.Form):
    blood_group_needed = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Blood Group')] + BloodRequest._meta.get_field('blood_group_needed').choices,
        widget=forms.Select(attrs={'class': SELECT})
    )
    urgency = forms.ChoiceField(required=False, choices=[('', 'Any Urgency')] + BloodRequest.Urgency.choices,
                                 widget=forms.Select(attrs={'class': SELECT}))
    status = forms.ChoiceField(required=False, choices=[('', 'Any Status')] + BloodRequest.Status.choices,
                                widget=forms.Select(attrs={'class': SELECT}))
