from django.core.cache import cache

from donors.models import Donor
from blood_requests.models import BloodRequest


def site_stats_processor(request):
    """Small, cached site-wide stats for the footer / any page that wants
    them, so we don't run 3 extra queries on every single request."""
    stats = cache.get('site_stats')
    if stats is None:
        stats = {
            'stat_available_donors': Donor.objects.filter(is_available=True).count(),
            'stat_total_requests': BloodRequest.objects.count(),
            'stat_cities_covered': Donor.objects.values('district').distinct().count(),
        }
        cache.set('site_stats', stats, 300)  # 5 minutes
    return stats
