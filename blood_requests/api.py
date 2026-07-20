from rest_framework import serializers, viewsets

from .models import BloodRequest


class BloodRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)

    class Meta:
        model = BloodRequest
        fields = [
            'id', 'patient_name', 'hospital', 'blood_group_needed', 'units_needed',
            'urgency', 'status', 'required_date', 'location', 'requested_by_name', 'created_at',
        ]


class BloodRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only feed of open blood requests."""
    queryset = BloodRequest.objects.filter(status=BloodRequest.Status.OPEN).select_related('requested_by')
    serializer_class = BloodRequestSerializer
    filterset_fields = ['blood_group_needed', 'urgency']
