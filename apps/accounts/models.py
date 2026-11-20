from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.validators import validate_avatar_image

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"

class Designation(models.Model):
    title = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations', null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=1, help_text="Seniority/Pay grade level")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        unique_together = ('title', 'department')
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'

    def __str__(self):
        dept_str = f" - {self.department.code}" if self.department else ""
        return f"{self.title}{dept_str}"

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        TRAINER = 'TRAINER', 'Trainer / Instructor'
        EMPLOYEE = 'EMPLOYEE', 'Employee / Learner'

    class ApprovalStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    approval_status = models.CharField(
        max_length=20, 
        choices=ApprovalStatus.choices, 
        default=ApprovalStatus.PENDING
    )
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    designation = models.ForeignKey(
        Designation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    rejection_reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_trainer_role(self):
        return self.role == self.Role.TRAINER

    def is_employee_role(self):
        return self.role == self.Role.EMPLOYEE

    def is_approved(self):
        return self.approval_status == self.ApprovalStatus.APPROVED or self.is_superuser

    def get_full_name_or_username(self):
        full = self.get_full_name()
        return full if full else self.username

    def __str__(self):
        return f"{self.username} [{self.get_role_display()}]"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    qualifications = models.TextField(blank=True, help_text="Degrees, certifications, diplomas")
    experience_years = models.PositiveIntegerField(default=0)
    areas_of_interest = models.TextField(blank=True, help_text="e.g. AI, Climate Modeling, Remote Sensing")
    learning_objectives = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='profiles/employees/', blank=True, null=True, validators=[validate_avatar_image])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employee Profile: {self.user.username} ({self.employee_id or 'No ID'})"

class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer_profile')
    qualifications = models.TextField(blank=True, help_text="Academic & Professional Qualifications")
    experience_years = models.PositiveIntegerField(default=0)
    areas_of_expertise = models.TextField(blank=True, help_text="Primary domain expertise")
    biography = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='profiles/trainers/', blank=True, null=True, validators=[validate_avatar_image])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trainer Profile: {self.user.username}"

