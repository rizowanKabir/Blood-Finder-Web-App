from django.contrib import admin

from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'blood_group', 'division', 'district',
                     'is_available', 'is_featured', 'total_donations', 'created_at']
    list_filter = ['blood_group', 'division', 'is_available', 'is_featured', 'gender']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'district', 'area']
    list_editable = ['is_available', 'is_featured']
    autocomplete_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Account', {'fields': ('user',)}),
        ('Personal', {'fields': ('age', 'gender', 'weight', 'occupation')}),
        ('Donation', {'fields': ('blood_group', 'is_available', 'is_featured', 'last_donation_date', 'total_donations', 'medical_notes')}),
        ('Location', {'fields': ('division', 'district', 'area', 'address')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    @admin.display(description='Name')
    def get_full_name(self, obj):
        return obj.get_full_name()
