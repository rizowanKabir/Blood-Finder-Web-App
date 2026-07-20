from rest_framework import serializers, viewsets

from .models import Donor


class DonorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_eligible_to_donate = serializers.BooleanField(read_only=True)

    class Meta:
        model = Donor
        fields = [
            'id', 'full_name', 'blood_group', 'division', 'district', 'area',
            'is_available', 'is_featured', 'is_eligible_to_donate', 'total_donations', 'created_at',
        ]


class DonorViewSet(viewsets.ReadOnlyModelViewSet):
    """Public, read-only donor directory API — DRF structure ready for a
    future mobile client or partner integration."""
    queryset = Donor.objects.select_related('user').all()
    serializer_class = DonorSerializer
    filterset_fields = ['blood_group', 'division', 'is_available']
