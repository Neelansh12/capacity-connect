from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import models
from .models import Certificate
from .services import generate_certificate_pdf_buffer, issue_certificate_if_eligible
from apps.courses.models import Enrollment

def certificate_verify_view(request):
    """
    Public Certificate Verification Portal.
    Allows employers, departments, or auditors to verify authenticity.
    """
    cert_id = request.GET.get('id', '').strip()
    certificate = None
    searched = False
    is_valid = False

    if cert_id:
        searched = True
        certificate = Certificate.objects.filter(
            models.Q(certificate_id__iexact=cert_id) | models.Q(verification_code__iexact=cert_id)
        ).select_related('enrollment__employee', 'enrollment__course', 'enrollment__employee__department').first()
        is_valid = certificate is not None

    return render(request, 'certificates/verify.html', {
        'searched': searched,
        'is_valid': is_valid,
        'certificate': certificate,
        'query_id': cert_id,
    })

@login_required
def certificate_view(request, cert_id):
    """HTML preview of an issued certificate."""
    certificate = get_object_or_404(
        Certificate.objects.select_related('enrollment__employee', 'enrollment__course', 'enrollment__course__trainer'),
        certificate_id=cert_id
    )

    is_owner = (certificate.employee == request.user)
    is_trainer = (certificate.course.trainer == request.user)
    is_admin = request.user.is_admin_role()

    if not (is_owner or is_trainer or is_admin):
        raise PermissionDenied("You do not have permission to view this certificate.")

    return render(request, 'certificates/view.html', {
        'certificate': certificate,
    })

@login_required
def certificate_download_view(request, cert_id):
    """Download the Certificate as a PDF."""
    certificate = get_object_or_404(
        Certificate.objects.select_related('enrollment__employee', 'enrollment__course', 'enrollment__course__trainer'),
        certificate_id=cert_id
    )

    is_owner = (certificate.employee == request.user)
    is_trainer = (certificate.course.trainer == request.user)
    is_admin = request.user.is_admin_role()

    if not (is_owner or is_trainer or is_admin):
        raise PermissionDenied("You do not have permission to download this certificate.")

    # Generate buffer on the fly if file not already on disk
    if certificate.pdf_file and certificate.pdf_file.storage.exists(certificate.pdf_file.name):
        response = HttpResponse(certificate.pdf_file.read(), content_type='application/pdf')
    else:
        pdf_buffer = generate_certificate_pdf_buffer(certificate)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')

    response['Content-Disposition'] = f'attachment; filename="Certificate-{certificate.certificate_id}.pdf"'
    return response

@login_required
def request_certificate_view(request, enrollment_id):
    """Manual request/trigger to claim certificate if eligible."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, employee=request.user)
    cert = issue_certificate_if_eligible(enrollment)
    if cert:
        messages.success(request, "Certificate issued successfully!")
        return redirect('certificates:view', cert_id=cert.certificate_id)
    else:
        messages.error(request, "You are not yet eligible for a certificate. Please complete all modules and pass required assessments.")
        return redirect('courses:learn', slug=enrollment.course.slug)
