from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Announcement(models.Model):
    class Type(models.TextChoices):
        GENERAL = 'GENERAL', 'General Notice'
        TRAINING = 'TRAINING', 'Training Program'
        URGENT = 'URGENT', 'Important Alert'
        ACHIEVEMENT = 'ACHIEVEMENT', 'Milestone & Achievement'

    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=Type.choices, default=Type.GENERAL)
    is_public = models.BooleanField(default=True, help_text="Show on public landing page")
    is_pinned = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"[{self.get_announcement_type_display()}] {self.title}"

class Notification(models.Model):
    class Type(models.TextChoices):
        APPROVAL = 'APPROVAL', 'Account Approval'
        ENROLLMENT = 'ENROLLMENT', 'Course Enrollment'
        ASSESSMENT = 'ASSESSMENT', 'Assessment Alert'
        CERTIFICATE = 'CERTIFICATE', 'Certificate Issued'
        ANNOUNCEMENT = 'ANNOUNCEMENT', 'Announcement'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.ENROLLMENT)
    target_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.user.username}: {self.title}"

class CourseFeedback(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='feedbacks')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_feedbacks')
    course_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 to 5 Stars"
    )
    trainer_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 to 5 Stars"
    )
    comments = models.TextField(help_text="Course content feedback")
    improvement_suggestions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'employee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.username} on {self.course.title} ({self.course_rating}/5)"

class TrainerResource(models.Model):
    class Category(models.TextChoices):
        RESEARCH_PAPER = 'RESEARCH_PAPER', 'Research Paper / Publication'
        DATASET = 'DATASET', 'Scientific Dataset / Specimen Data'
        MANUAL = 'MANUAL', 'Technical Manual / SOP'
        POLICY_DOC = 'POLICY_DOC', 'Government Policy & Guidelines'
        PRESENTATION = 'PRESENTATION', 'Training Slide Deck'

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.MANUAL)
    file = models.FileField(upload_to='resources/library/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_library_resources')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_category_display()}]"

