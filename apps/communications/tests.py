from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, Department
from .models import Announcement, Notification

class CommunicationsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IITM Pune", code="IITM")
        self.user = User.objects.create_user(
            username='comm_user',
            password='Password@123',
            role=User.Role.EMPLOYEE,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

    def test_view_names_match_specification(self):
        """Verify announcements_view and notifications_view match report specification (Page 22)."""
        from apps.communications.views import announcements_view, notifications_view
        self.assertTrue(callable(announcements_view))
        self.assertTrue(callable(notifications_view))

    def test_realtime_notification_api(self):
        """Verify real-time notification endpoint returns live JSON count and alerts."""
        Notification.objects.create(
            user=self.user,
            title="New Course Available",
            message="Check out the new Oceanography course.",
            notification_type=Notification.Type.ANNOUNCEMENT
        )

        self.client.login(username='comm_user', password='Password@123')
        res = self.client.get(reverse('communications:notifications_unread_api'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['unread_count'], 1)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], "New Course Available")

    def test_notification_get_does_not_mutate_unread_state(self):
        """Verify GET does not unconditionally mark unread notifications as read (idempotency fix)."""
        Notification.objects.create(
            user=self.user,
            title="Important Alert",
            message="Read this notice.",
            is_read=False
        )
        self.client.login(username='comm_user', password='Password@123')

        # Visiting the page via GET must not mutate database
        res = self.client.get(reverse('communications:notifications'))
        self.assertEqual(res.status_code, 200)

        notif = self.user.notifications.first()
        self.assertFalse(notif.is_read)

        # POST with mark_all_read should mark as read
        post_res = self.client.post(reverse('communications:notifications'), {'action': 'mark_all_read'})
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

