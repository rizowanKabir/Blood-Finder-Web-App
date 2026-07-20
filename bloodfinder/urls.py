from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from donors.api import DonorViewSet
from blood_requests.api import BloodRequestViewSet

admin.site.site_header = 'Blood Finder Administration'
admin.site.site_title = 'Blood Finder Admin'
admin.site.index_title = 'Manage Users, Donors, Requests & Locations'

router = DefaultRouter()
router.register('donors', DonorViewSet, basename='api-donors')
router.register('requests', BloodRequestViewSet, basename='api-requests')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('donors/', include('donors.urls')),
    path('requests/', include('blood_requests.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
