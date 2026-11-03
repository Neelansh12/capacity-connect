from apps.communications.models import Notification, Announcement

def portal_context(request):
    """Global template context for user notifications, unread counts, and active announcements."""
    unread_notifications_count = 0
    recent_notifications = []

    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        recent_notifications = request.user.notifications.all()[:5]

    pinned_announcements = Announcement.objects.filter(is_pinned=True)[:2]

    return {
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
        'pinned_announcements': pinned_announcements,
        'PORTAL_NAME': 'Capacity Connect',
        'PORTAL_TAGLINE': 'Learn. Develop. Connect. Grow.',
        'PORTAL_ORGANIZATION': 'Ministry of Earth Sciences (MoES)',
    }

