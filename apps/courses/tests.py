from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from apps.accounts.models import User, Department
from .models import Category, Course, CourseModule, Enrollment, ModuleProgress

class CoursesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="INCOIS", code="INCOIS")
        
        self.trainer = User.objects.create_user(
            username='trainer_c',
            password='Password@123',
            role=User.Role.TRAINER,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.employee = User.objects.create_user(
            username='employee_c',
            password='Password@123',
            role=User.Role.EMPLOYEE,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.category = Category.objects.create(name="Oceanography", slug="oceanography")

        self.course = Course.objects.create(
            title="Satellite Oceanography",
            slug="satellite-oceanography",
            trainer=self.trainer,
            category=self.category,
            difficulty_level=Course.Difficulty.INTERMEDIATE,
            status=Course.Status.PUBLISHED,
            description="Testing course description."
        )

        self.mod1 = CourseModule.objects.create(course=self.course, title="Module 1", order=1, is_mandatory=True)
        self.mod2 = CourseModule.objects.create(course=self.course, title="Module 2", order=2, is_mandatory=True)

    def test_enrollment_and_duplicate_prevention(self):
        self.client.login(username='employee_c', password='Password@123')
        # First enrollment
        response = self.client.post(reverse('courses:enroll', kwargs={'slug': self.course.slug}))
        self.assertRedirects(response, reverse('courses:learn', kwargs={'slug': self.course.slug}))
        self.assertEqual(Enrollment.objects.filter(employee=self.employee, course=self.course).count(), 1)

        # Database unique constraint test
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(employee=self.employee, course=self.course)

    def test_genuine_progress_calculation(self):
        enrollment = Enrollment.objects.create(employee=self.employee, course=self.course)
        mp1 = ModuleProgress.objects.create(enrollment=enrollment, module=self.mod1)
        mp2 = ModuleProgress.objects.create(enrollment=enrollment, module=self.mod2)

        # Initially 0%
        self.assertEqual(enrollment.progress_percentage, 0.0)

        # Complete module 1
        mp1.mark_as_completed()
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress_percentage, 50.0)

        # Complete module 2
        mp2.mark_as_completed()
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress_percentage, 100.0)
        self.assertTrue(enrollment.is_completed)

    def test_view_name_matching_specification(self):
        """Verify enroll_view and learn_view match report specification."""
        from apps.courses.views import enroll_view, learn_view
        self.assertTrue(callable(enroll_view))
        self.assertTrue(callable(learn_view))

