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

    def test_first_user_registration_bootstraps_admin(self):
        """Verify report specification: first registered user becomes ADMIN and superuser."""
        User.objects.all().delete()
        self.assertEqual(User.objects.count(), 0)

        # Register first user (submits as employee, bootstrapped by system as admin)
        reg_data = {
            'username': 'first_admin',
            'email': 'first@moes.gov.in',
            'first_name': 'First',
            'last_name': 'Admin',
            'role': User.Role.EMPLOYEE,
            'department': self.dept.id,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
        }
        res1 = self.client.post(reverse('accounts:register'), reg_data)
        self.assertEqual(res1.status_code, 302)

        first_user = User.objects.get(username='first_admin')
        self.assertEqual(first_user.role, User.Role.ADMIN)
        self.assertTrue(first_user.is_staff)
        self.assertTrue(first_user.is_superuser)
        self.assertEqual(first_user.approval_status, User.ApprovalStatus.APPROVED)

        # Register second user (must remain standard pending employee)
        reg_data_2 = {
            'username': 'second_emp',
            'email': 'second@moes.gov.in',
            'first_name': 'Second',
            'last_name': 'Employee',
            'role': User.Role.EMPLOYEE,
            'department': self.dept.id,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
        }
        res2 = self.client.post(reverse('accounts:register'), reg_data_2)
        self.assertEqual(res2.status_code, 302)

        second_user = User.objects.get(username='second_emp')
        self.assertEqual(second_user.role, User.Role.EMPLOYEE)
        self.assertFalse(second_user.is_staff)
        self.assertFalse(second_user.is_superuser)
        self.assertEqual(second_user.approval_status, User.ApprovalStatus.PENDING)

