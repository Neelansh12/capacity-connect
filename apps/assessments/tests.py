from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, Department
from apps.courses.models import Course, Enrollment
from .models import Assessment, Question, AnswerOption, AssessmentAttempt

class AssessmentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IITM", code="IITM")
        
        self.trainer = User.objects.create_user(
            username='trainer_a',
            password='Password@123',
            role=User.Role.TRAINER,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.employee = User.objects.create_user(
            username='employee_a',
            password='Password@123',
            role=User.Role.EMPLOYEE,
            approval_status=User.ApprovalStatus.APPROVED,
            department=self.dept
        )

        self.course = Course.objects.create(
            title="Climate Dynamics",
            slug="climate-dynamics",
            trainer=self.trainer,
            status=Course.Status.PUBLISHED,
            description="Testing course."
        )

        self.enrollment = Enrollment.objects.create(employee=self.employee, course=self.course)

        self.assessment = Assessment.objects.create(
            course=self.course,
            title="Climate Dynamics Exam",
            passing_percentage=50,
            duration_minutes=15,
            max_attempts=2,
            is_published=True
        )

        self.q1 = Question.objects.create(assessment=self.assessment, question_text="What does ENSO stand for?", marks=2, order=1)
        self.opt1_correct = AnswerOption.objects.create(question=self.q1, option_text="El Nino Southern Oscillation", is_correct=True, order=1)
        self.opt1_wrong = AnswerOption.objects.create(question=self.q1, option_text="Eastern North Sea Organization", is_correct=False, order=2)

    def test_assessment_server_side_evaluation_and_pass(self):
        self.client.login(username='employee_a', password='Password@123')
        
        # Submit correct answer
        post_data = {
            f'question_{self.q1.id}': str(self.opt1_correct.id)
        }
        response = self.client.post(reverse('assessments:take', kwargs={'course_slug': self.course.slug}), post_data)
        
        attempt = AssessmentAttempt.objects.filter(assessment=self.assessment, employee=self.employee).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score_obtained, 2.0)
        self.assertEqual(attempt.percentage_obtained, 100.0)
        self.assertTrue(attempt.passed)

    def test_assessment_attempt_limit_enforcement(self):
        # Create 2 previous attempts
        AssessmentAttempt.objects.create(assessment=self.assessment, employee=self.employee, attempt_number=1, score_obtained=0, total_marks=2, percentage_obtained=0, passed=False)
        AssessmentAttempt.objects.create(assessment=self.assessment, employee=self.employee, attempt_number=2, score_obtained=0, total_marks=2, percentage_obtained=0, passed=False)

        self.client.login(username='employee_a', password='Password@123')
        # Third attempt should be blocked
        response = self.client.get(reverse('assessments:take', kwargs={'course_slug': self.course.slug}))
        self.assertRedirects(response, reverse('assessments:detail', kwargs={'course_slug': self.course.slug}))

    def test_view_name_matching_specification(self):
        """Verify that take_assessment_view and submit_assessment_view match report specification."""
        from apps.assessments.views import take_assessment_view, submit_assessment_view
        self.assertTrue(callable(take_assessment_view))
        self.assertTrue(callable(submit_assessment_view))

    def test_assessment_server_timer_timeout_enforcement(self):
        """Verify server enforces duration limit when submission time has expired."""
        from datetime import timedelta
        from django.utils import timezone

        self.client.login(username='employee_a', password='Password@123')

        # Simulate assessment start 20 minutes ago (allowed: 15 minutes)
        session = self.client.session
        past_time = timezone.now() - timedelta(minutes=20)
        session[f'assessment_start_{self.assessment.id}'] = past_time.isoformat()
        session.save()

        post_data = {
            f'question_{self.q1.id}': str(self.opt1_correct.id)
        }
        response = self.client.post(reverse('assessments:submit', kwargs={'course_slug': self.course.slug}), post_data)

        attempt = AssessmentAttempt.objects.filter(assessment=self.assessment, employee=self.employee).first()
        self.assertIsNotNone(attempt)
        self.assertTrue(attempt.is_timed_out)
        self.assertFalse(attempt.passed)

