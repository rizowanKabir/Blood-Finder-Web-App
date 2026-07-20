from django.urls import path

from . import views

app_name = 'donors'

urlpatterns = [
    path('', views.DonorListView.as_view(), name='list'),
    path('search-api/', views.quick_search_api, name='quick_search_api'),
    path('become-a-donor/', views.DonorCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DonorDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DonorUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DonorDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle-availability/', views.toggle_availability, name='toggle_availability'),
]
