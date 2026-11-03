from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Competency(models.Model):
    class Domain(models.TextChoices):
        SCIENTIFIC = 'SCIENTIFIC', 'Earth & Climate Sciences'
        TECHNICAL = 'TECHNICAL', 'Technical & Software'
        MANAGERIAL = 'MANAGERIAL', 'Administrative & Leadership'
        OPERATIONAL = 'OPERATIONAL', 'Field Operations & Instruments'

    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    domain = models.CharField(max_length=30, choices=Domain.choices, default=Domain.TECHNICAL)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Competency'
        verbose_name_plural = 'Competencies'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [{self.get_domain_display()}]"

class Proficiency(models.TextChoices):
    BEGINNER = 'BEGINNER', 'Beginner (Level 1)'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermediate (Level 2)'
    ADVANCED = 'ADVANCED', 'Advanced (Level 3)'
    EXPERT = 'EXPERT', 'Expert (Level 4)'

class TrainerCompetency(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='trainer_competencies',
        limit_choices_to={'role__in': ['TRAINER', 'ADMIN']}
    )
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='trainer_mappings')
    proficiency_level = models.CharField(max_length=20, choices=Proficiency.choices, default=Proficiency.INTERMEDIATE)
    experience_years = models.PositiveIntegerField(default=1, help_text="Years applying this competency")
    supporting_description = models.TextField(blank=True, help_text="Key achievements, projects, papers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trainer', 'competency')
        ordering = ['-proficiency_level', 'competency__name']

    def get_proficiency_weight(self):
        weights = {
            Proficiency.BEGINNER: 1.0,
            Proficiency.INTERMEDIATE: 2.0,
            Proficiency.ADVANCED: 3.0,
            Proficiency.EXPERT: 4.0,
        }
        return weights.get(self.proficiency_level, 1.0)

    def __str__(self):
        return f"{self.trainer.username} - {self.competency.name} ({self.proficiency_level})"

class EmployeeCompetency(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='employee_competencies',
        limit_choices_to={'role__in': ['EMPLOYEE', 'ADMIN']}
    )
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='employee_mappings')
    proficiency_level = models.CharField(max_length=20, choices=Proficiency.choices, default=Proficiency.BEGINNER)
    is_target_skill = models.BooleanField(default=False, help_text="True if employee is looking to develop this skill")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'competency')

    def __str__(self):
        status = "Target" if self.is_target_skill else "Current"
        return f"{self.employee.username} - {self.competency.name} [{status}]"

class CourseCompetency(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='competency_outcomes')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='course_outcomes')
    target_proficiency = models.CharField(max_length=20, choices=Proficiency.choices, default=Proficiency.INTERMEDIATE)

    class Meta:
        unique_together = ('course', 'competency')

    def __str__(self):
        return f"{self.course.title} -> {self.competency.name} ({self.target_proficiency})"

