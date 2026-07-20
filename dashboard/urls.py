from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('activity/', views.MyActivityView.as_view(), name='my_activity'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('admin-stats/', views.AdminDashboardView.as_view(), name='admin_stats'),
    path('admin-stats/api/', views.admin_stats_api, name='admin_stats_api'),
]
