from django.urls import path

from . import views

app_name = 'blood_requests'

urlpatterns = [
    path('', views.BloodRequestListView.as_view(), name='list'),
    path('new/', views.BloodRequestCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BloodRequestDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BloodRequestUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BloodRequestDeleteView.as_view(), name='delete'),
    path('<int:pk>/accept/', views.accept_request, name='accept'),
    path('<int:pk>/complete/', views.complete_request, name='complete'),
]
