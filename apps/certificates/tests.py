from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, Department
from apps.courses.models import Course, CourseModule, Enrollment, ModuleProgress
from apps.assessments.models import Assessment, AssessmentAttempt
from .models import Certificate
from .services import check_certificate_eligibility, issue_certificate_if_eligible, generate_certificate_pdf_buffer

class CertificatesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IMD", code="IMD")
        
        self.trainer = User.objects.create_user(
            username='trainer_cert',
            password='Password@123',
            role=User.Role.TRAINER,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.employee = User.objects.create_user(
            username='employee_cert',
            password='Password@123',
            role=User.Role.EMPLOYEE,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.course = Course.objects.create(
            title="Radar Meteorology",
            slug="radar-meteorology",
            trainer=self.trainer,
            status=Course.Status.PUBLISHED,
            description="Testing course."
        )

        self.mod1 = CourseModule.objects.create(course=self.course, title="Mod 1", order=1, is_mandatory=True)
        self.enrollment = Enrollment.objects.create(employee=self.employee, course=self.course)

    def test_certificate_eligibility_enforcement(self):
        # 1. Incomplete module progress -> not eligible
        is_elig, reason = check_certificate_eligibility(self.enrollment)
        self.assertFalse(is_elig)

        # 2. Mark module complete -> 100% progress
        mp = ModuleProgress.objects.create(enrollment=self.enrollment, module=self.mod1)
        mp.mark_as_completed()
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100.0)

        # 3. If mandatory assessment added, must pass it before eligible
        assessment = Assessment.objects.create(course=self.course, title="Radar Exam", is_published=True, passing_percentage=60)
        is_elig, reason = check_certificate_eligibility(self.enrollment)
        self.assertFalse(is_elig)

        # 4. Pass assessment
        AssessmentAttempt.objects.create(assessment=assessment, employee=self.employee, attempt_number=1, score_obtained=10, total_marks=10, percentage_obtained=100.0, passed=True)
        is_elig, reason = check_certificate_eligibility(self.enrollment)
        self.assertTrue(is_elig)

    def test_certificate_issuance_and_pdf_generation(self):
        # Setup complete enrollment
        mp = ModuleProgress.objects.create(enrollment=self.enrollment, module=self.mod1)
        mp.mark_as_completed()
        self.enrollment.refresh_from_db()

        cert = issue_certificate_if_eligible(self.enrollment)
        self.assertIsNotNone(cert)
        self.assertTrue(cert.certificate_id.startswith('CC-2026-'))

        # Verify PDF buffer generation works without errors
        pdf_buffer = generate_certificate_pdf_buffer(cert)
        self.assertGreater(len(pdf_buffer.getvalue()), 1000)

        # Duplicate issuance prevention
        cert2 = issue_certificate_if_eligible(self.enrollment)
        self.assertEqual(cert.id, cert2.id)

    def test_public_certificate_verification(self):
        cert = Certificate.objects.create(enrollment=self.enrollment)
        
        response = self.client.get(reverse('certificates:verify'), {'id': cert.certificate_id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Official Certificate Authenticated & Valid")
        self.assertContains(response, cert.certificate_id)

