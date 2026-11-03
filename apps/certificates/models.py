import uuid
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone

def generate_cert_id():
    token = secrets.token_hex(4).upper()
    return f"CC-2026-{token[:4]}-{token[4:]}"

def generate_verification_code():
    return uuid.uuid4().hex[:16].upper()

class Certificate(models.Model):
    enrollment = models.OneToOneField(
        'courses.Enrollment', 
        on_delete=models.CASCADE, 
        related_name='certificate'
    )
    certificate_id = models.CharField(max_length=50, unique=True, default=generate_cert_id)
    verification_code = models.CharField(max_length=64, unique=True, default=generate_verification_code)
    issued_at = models.DateTimeField(default=timezone.now)
    authorized_signatory = models.CharField(
        max_length=150, 
        default="Director General / Head of Capacity Building, MoES"
    )
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    class Meta:
        ordering = ['-issued_at']

    @property
    def employee(self):
        return self.enrollment.employee

    @property
    def course(self):
        return self.enrollment.course

    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.employee.username} ({self.course.title})"

