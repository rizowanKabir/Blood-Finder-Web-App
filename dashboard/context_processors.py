def notifications_processor(request):
    """Exposes the unread notification count to every template (navbar bell)."""
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
