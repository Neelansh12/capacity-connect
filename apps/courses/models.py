from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=50, default='book-open', help_text="Lucide icon name")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Course Category'
        verbose_name_plural = 'Course Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Course(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        ARCHIVED = 'ARCHIVED', 'Archived'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='authored_courses',
        limit_choices_to={'role__in': ['TRAINER', 'ADMIN']}
    )
    difficulty_level = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    estimated_duration_hours = models.PositiveIntegerField(default=10, help_text="Estimated training hours")
    learning_objectives = models.TextField(help_text="Key takeaways and learning objectives")
    prerequisites = models.TextField(blank=True, help_text="Recommended prior knowledge")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_modules_count(self):
        return self.modules.count()

    def get_enrollments_count(self):
        return self.enrollments.count()

    def __str__(self):
        return self.title

class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('course', 'order')

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"

class LearningResource(models.Model):
    class ResourceType(models.TextChoices):
        VIDEO = 'VIDEO', 'Video Lecture'
        PDF = 'PDF', 'PDF Document'
        PRESENTATION = 'PRESENTATION', 'PPT/Presentation'
        TEXT = 'TEXT', 'Text / Article Content'
        EXTERNAL_LINK = 'EXTERNAL_LINK', 'External Web Resource'

    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices, default=ResourceType.PDF)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    external_url = models.URLField(blank=True, help_text="e.g. YouTube, MoES archive, documentation")
    text_content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"

class Enrollment(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'course')
        ordering = ['-enrolled_at']

    def calculate_progress(self):
        total_modules = self.course.modules.count()
        if total_modules == 0:
            return 100.0 if self.is_completed else 0.0

        completed_count = self.module_progress.filter(is_completed=True).count()
        progress = round((completed_count / total_modules) * 100.0, 1)
        self.progress_percentage = min(progress, 100.0)

        # Check if all modules are complete
        if self.progress_percentage >= 100.0 and not self.is_completed:
            # If course has assessment, certificate eligibility handles completion; else mark complete
            has_mandatory_assessment = hasattr(self.course, 'assessment') and self.course.assessment.is_published
            if not has_mandatory_assessment:
                self.is_completed = True
                self.completed_at = timezone.now()

        self.save()
        return self.progress_percentage

    def __str__(self):
        return f"{self.employee.username} -> {self.course.title} ({self.progress_percentage}%)"

class ModuleProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'module')

    def mark_as_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
        self.enrollment.calculate_progress()

    def __str__(self):
        status = "Completed" if self.is_completed else "Incomplete"
        return f"{self.enrollment.employee.username} - {self.module.title} [{status}]"

