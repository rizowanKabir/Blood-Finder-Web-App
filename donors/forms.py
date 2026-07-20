from django import forms

from .models import Donor

INPUT = 'form-control custom-input'
SELECT = 'form-select custom-input'


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'age', 'gender', 'blood_group', 'division', 'district', 'area', 'address',
            'last_donation_date', 'is_available', 'weight', 'occupation', 'medical_notes',
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'class': INPUT, 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': SELECT}),
            'blood_group': forms.Select(attrs={'class': SELECT}),
            'division': forms.Select(attrs={'class': SELECT, 'id': 'id_division'}),
            'district': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. Any'}),
            'area': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. Any'}),
            'address': forms.Textarea(attrs={'class': INPUT, 'rows': 3, 'placeholder': 'Full address'}),
            'last_donation_date': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'weight': forms.NumberInput(attrs={'class': INPUT, 'placeholder': 'Weight in kg', 'step': '0.1'}),
            'occupation': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Occupation (optional)'}),
            'medical_notes': forms.Textarea(attrs={'class': INPUT, 'rows': 3, 'placeholder': 'Any relevant medical notes (optional)'}),
        }


class DonorSearchForm(forms.Form):
    """GET-based filter form powering the donor directory search."""
    blood_group = forms.ChoiceField(required=False, choices=[('', 'Any Blood Group')] + Donor._meta.get_field('blood_group').choices,
                                     widget=forms.Select(attrs={'class': SELECT}))
    division = forms.ChoiceField(required=False, choices=[('', 'Any Division')] + Donor._meta.get_field('division').choices,
                                  widget=forms.Select(attrs={'class': SELECT}))
    district = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': INPUT, 'placeholder': 'District'}))
    area = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': INPUT, 'placeholder': 'Area'}))
    available_only = forms.BooleanField(required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
