from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Department, Designation, EmployeeProfile, TrainerProfile

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="India Meteorological Department", code="IMD")
        self.desig = Designation.objects.create(title="Scientist 'B'", department=self.dept, level=1)
        
        # Approved Admin
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.gov.in',
            password='Password@123',
            role=User.Role.ADMIN,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        # Approved Trainer
        self.trainer = User.objects.create_user(
            username='trainer_test',
            email='trainer@test.gov.in',
            password='Password@123',
            role=User.Role.TRAINER,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )
        TrainerProfile.objects.create(user=self.trainer, experience_years=5)

        # Approved Employee
        self.employee = User.objects.create_user(
            username='employee_test',
            email='employee@test.gov.in',
            password='Password@123',
            role=User.Role.EMPLOYEE,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )
        EmployeeProfile.objects.create(user=self.employee, employee_id='EMP-TEST-01')

        # Unapproved Employee
        self.pending_user = User.objects.create_user(
            username='pending_test',
            email='pending@test.gov.in',
            password='Password@123',
            role=User.Role.EMPLOYEE,
            approval_status=User.ApprovalStatus.PENDING,
            department=self.dept
        )

    def test_user_roles(self):
        self.assertTrue(self.admin.is_admin_role())
        self.assertFalse(self.admin.is_employee_role())
        self.assertTrue(self.trainer.is_trainer_role())
        self.assertTrue(self.employee.is_employee_role())

    def test_unapproved_user_redirect(self):
        self.client.login(username='pending_test', password='Password@123')
        response = self.client.get(reverse('analytics:employee_dashboard'))
        self.assertRedirects(response, reverse('accounts:pending_approval'))

    def test_admin_approval_workflow(self):
        self.client.login(username='admin_test', password='Password@123')
        response = self.client.post(
            reverse('accounts:admin_user_approval', kwargs={'user_id': self.pending_user.id}),
            {'action': 'approve'}
        )
        self.pending_user.refresh_from_db()
        self.assertEqual(self.pending_user.approval_status, User.ApprovalStatus.APPROVED)

    def test_role_based_access_restriction(self):
        self.client.login(username='employee_test', password='Password@123')
        # Employee should be forbidden from admin dashboard
        response = self.client.get(reverse('analytics:admin_dashboard'))
        self.assertEqual(response.status_code, 403)

