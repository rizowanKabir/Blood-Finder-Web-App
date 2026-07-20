from django.contrib import admin
from django.utils.html import format_html

from .models import BloodRequest


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group_needed', 'colored_urgency', 'hospital',
                     'status', 'required_date', 'requested_by', 'created_at']
    list_filter = ['status', 'urgency', 'blood_group_needed']
    search_fields = ['patient_name', 'hospital', 'location', 'contact_person', 'contact_phone']
    list_editable = ['status']
    autocomplete_fields = ['requested_by', 'accepted_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    @admin.display(description='Urgency')
    def colored_urgency(self, obj):
        colors = {'normal': '#0099CC', 'urgent': '#FF9800', 'emergency': '#FF4F8B'}
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            colors.get(obj.urgency, '#1F2937'), obj.get_urgency_display()
        )
