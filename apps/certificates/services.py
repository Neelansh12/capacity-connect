"""
Certificate Generation & Verification Services
ReportLab PDF Generation with Capacity Connect Branding
"""

import io
import os
import unicodedata
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Certificate
from apps.assessments.models import AssessmentAttempt

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

for ttf_path, name in [
    ("C:/Windows/Fonts/arial.ttf", "ArialUnicode"),
    ("C:/Windows/Fonts/arialbd.ttf", "ArialUnicode-Bold")
]:
    if os.path.exists(ttf_path):
        try:
            pdfmetrics.registerFont(TTFont(name, ttf_path))
            if name == "ArialUnicode":
                FONT_REGULAR = "ArialUnicode"
            elif name == "ArialUnicode-Bold":
                FONT_BOLD = "ArialUnicode-Bold"
        except Exception:
            pass

def safe_str(val):
    """Sanitize string for ReportLab drawing, normalizing non-latin1 unicode characters."""
    if not val:
        return ""
    val = str(val)
    if FONT_REGULAR == "Helvetica":
        val = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode('ascii')
    return val

def check_certificate_eligibility(enrollment):
    """
    Checks if an employee is eligible for a certificate.
    Returns: (bool, str)
    """
    if hasattr(enrollment, 'certificate'):
        return True, "Certificate already issued."

    # 1. Check all modules completed
    total_modules = enrollment.course.modules.count()
    if total_modules > 0 and enrollment.progress_percentage < 100.0:
        return False, f"Course progress is {enrollment.progress_percentage}%. All modules must be completed."

    # 2. Check assessment if one exists
    has_assessment = hasattr(enrollment.course, 'assessment') and enrollment.course.assessment.is_published
    if has_assessment:
        passed_attempt = AssessmentAttempt.objects.filter(
            assessment=enrollment.course.assessment,
            employee=enrollment.employee,
            passed=True
        ).exists()
        if not passed_attempt:
            return False, "Passing the final course assessment is required."

    return True, "Eligible for certificate."

def issue_certificate_if_eligible(enrollment):
    """
    Automatically issues a certificate if eligible and generates the PDF.
    """
    if hasattr(enrollment, 'certificate'):
        return enrollment.certificate

    is_eligible, _ = check_certificate_eligibility(enrollment)
    if not is_eligible:
        return None

    # Create certificate record
    cert = Certificate.objects.create(
        enrollment=enrollment,
        issued_at=timezone.now()
    )

    # Generate PDF
    pdf_buffer = generate_certificate_pdf_buffer(cert)
    cert.pdf_file.save(f"{cert.certificate_id}.pdf", ContentFile(pdf_buffer.getvalue()), save=True)

    return cert

def generate_certificate_pdf_buffer(certificate):
    """
    Draws a professional Certificate PDF using ReportLab in Landscape orientation.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Background / Outer Border
    p.setStrokeColor(colors.HexColor('#0f172a')) # Navy
    p.setLineWidth(5)
    p.rect(20, 20, width - 40, height - 40)

    p.setStrokeColor(colors.HexColor('#0d9488')) # Teal accent
    p.setLineWidth(1.5)
    p.rect(26, 26, width - 52, height - 52)

    # Corner Decorative Marks
    corner_size = 20
    p.setStrokeColor(colors.HexColor('#0d9488'))
    p.setLineWidth(2)
    # Top-Left
    p.line(32, height - 32, 32 + corner_size, height - 32)
    p.line(32, height - 32, 32, height - 32 - corner_size)
    # Top-Right
    p.line(width - 32, height - 32, width - 32 - corner_size, height - 32)
    p.line(width - 32, height - 32, width - 32, height - 32 - corner_size)
    # Bottom-Left
    p.line(32, 32, 32 + corner_size, 32)
    p.line(32, 32, 32, 32 + corner_size)
    # Bottom-Right
    p.line(width - 32, 32, width - 32 - corner_size, 32)
    p.line(width - 32, 32, width - 32, 32 + corner_size)

    # Header Branding
    p.setFont(FONT_BOLD, 14)
    p.setFillColor(colors.HexColor('#0d9488'))
    p.drawCentredString(width / 2.0, height - 70, "MINISTRY OF EARTH SCIENCES — CAPACITY CONNECT")

    p.setFont(FONT_BOLD, 28)
    p.setFillColor(colors.HexColor('#0f172a'))
    p.drawCentredString(width / 2.0, height - 110, "CERTIFICATE OF COMPLETION")

    p.setFont(FONT_REGULAR, 11)
    p.setFillColor(colors.HexColor('#64748b'))
    p.drawCentredString(width / 2.0, height - 130, "Learn. Develop. Connect. Grow.")

    # Main Body Text
    p.setFont(FONT_REGULAR, 13)
    p.setFillColor(colors.HexColor('#334155'))
    p.drawCentredString(width / 2.0, height - 180, "This is proudly presented to")

    # Recipient Name
    employee_name = safe_str(certificate.employee.get_full_name() or certificate.employee.username)
    p.setFont(FONT_BOLD, 24)
    p.setFillColor(colors.HexColor('#0f172a'))
    p.drawCentredString(width / 2.0, height - 220, employee_name.upper())

    # Underline under recipient
    p.setStrokeColor(colors.HexColor('#cbd5e1'))
    p.setLineWidth(1)
    p.line(width / 2.0 - 180, height - 228, width / 2.0 + 180, height - 228)

    # Description
    p.setFont(FONT_REGULAR, 12)
    p.setFillColor(colors.HexColor('#475569'))
    p.drawCentredString(width / 2.0, height - 260, "for successfully completing the institutional capacity-building training program")

    # Course Title
    p.setFont(FONT_BOLD, 18)
    p.setFillColor(colors.HexColor('#0d9488'))
    p.drawCentredString(width / 2.0, height - 295, f'"{safe_str(certificate.course.title)}"')

    # Trainer and Department Info
    trainer_name = safe_str(certificate.course.trainer.get_full_name() or certificate.course.trainer.username)
    dept_name = safe_str(certificate.employee.department.name if certificate.employee.department else "Ministry of Earth Sciences")
    p.setFont(FONT_REGULAR, 11)
    p.setFillColor(colors.HexColor('#64748b'))
    p.drawCentredString(width / 2.0, height - 325, f"Lead Instructor: {trainer_name}  |  Department: {dept_name}")

    # Signatures & Verification Row
    p.setFont(FONT_BOLD, 10)
    p.setFillColor(colors.HexColor('#0f172a'))

    # Left: Issuance Date
    issue_date = certificate.issued_at.strftime('%d %B %Y')
    p.drawString(60, 95, f"Date of Issue: {issue_date}")
    p.setFont(FONT_REGULAR, 9)
    p.setFillColor(colors.HexColor('#64748b'))
    p.drawString(60, 80, "Capacity Building Commission / MoES")

    # Center: Certificate ID & Verification Code
    p.setFont(FONT_BOLD, 9)
    p.setFillColor(colors.HexColor('#0f172a'))
    p.drawCentredString(width / 2.0, 95, f"Certificate ID: {certificate.certificate_id}")
    p.setFont(FONT_REGULAR, 8)
    p.setFillColor(colors.HexColor('#64748b'))
    p.drawCentredString(width / 2.0, 80, f"Verify at /certificates/verify/?id={certificate.certificate_id}")

    # Right: Authorized Signatory
    p.setFont(FONT_BOLD, 10)
    p.setFillColor(colors.HexColor('#0f172a'))
    p.drawRightString(width - 60, 95, safe_str(certificate.authorized_signatory))
    p.setFont(FONT_REGULAR, 9)
    p.setFillColor(colors.HexColor('#64748b'))
    p.drawRightString(width - 60, 80, "Institutional Competency Authority")

    # Signature line
    p.setStrokeColor(colors.HexColor('#94a3b8'))
    p.setLineWidth(1)
    p.line(width - 240, 110, width - 60, 110)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

