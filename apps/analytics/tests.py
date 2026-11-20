from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, Department

class AnalyticsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="NCMRWF", code="NCMRWF")
        self.admin = User.objects.create_user(
            username='admin_analytics',
            password='Password@123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

    def test_admin_report_download_url_matches_specification(self):
        """Verify report download URL matches specification: /analytics/admin/report/download/ (Page 19)."""
        url = reverse('analytics:admin_report_pdf')
        self.assertEqual(url, '/analytics/admin/report/download/')

        self.client.login(username='admin_analytics', password='Password@123')
        res = self.client.get('/analytics/admin/report/download/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')

