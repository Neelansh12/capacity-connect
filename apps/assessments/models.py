from django.db import models
from django.conf import settings
from django.utils import timezone

class Assessment(models.Model):
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='assessment')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    passing_percentage = models.PositiveIntegerField(default=60, help_text="Minimum score percentage required to pass")
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Time allowed in minutes")
    max_attempts = models.PositiveIntegerField(default=2, help_text="Max attempts allowed per employee")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_active_now(self):
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return self.is_published

    def get_total_marks(self):
        return sum(q.marks for q in self.questions.all())

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}..."

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        status = "✓ Correct" if self.is_correct else "✗"
        return f"{self.option_text[:50]} [{status}]"

class AssessmentAttempt(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assessment_attempts'
    )
    attempt_number = models.PositiveIntegerField(default=1)
    score_obtained = models.FloatField(default=0.0)
    total_marks = models.FloatField(default=0.0)
    percentage_obtained = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('assessment', 'employee', 'attempt_number')

    def __str__(self):
        result = "PASSED" if self.passed else "FAILED"
        return f"{self.employee.username} - {self.assessment.title} (Attempt {self.attempt_number}: {self.percentage_obtained}% - {result})"

class SubmittedAnswer(models.Model):
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='submitted_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Attempt {self.attempt_id} - Q{self.question_id}: {'Correct' if self.is_correct else 'Incorrect'}"

