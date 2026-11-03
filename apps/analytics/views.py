import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment, CourseModule
from apps.assessments.models import Assessment, AssessmentAttempt
from apps.certificates.models import Certificate
from apps.competencies.models import Competency, EmployeeCompetency
from apps.communications.models import CourseFeedback, Announcement
from apps.accounts.models import Department
from apps.accounts.decorators import admin_required, trainer_required, employee_required
from .reports import generate_admin_report_pdf

User = get_user_model()

@admin_required
def admin_dashboard_view(request):
    """Platform-wide management and analytics dashboard."""
    # Summary Counters
    total_users = User.objects.count()
    total_trainers = User.objects.filter(role=User.Role.TRAINER).count()
    total_employees = User.objects.filter(role=User.Role.EMPLOYEE).count()
    pending_approvals = User.objects.filter(approval_status=User.ApprovalStatus.PENDING).count()

    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(status=Course.Status.PUBLISHED).count()
    total_enrollments = Enrollment.objects.count()
    completed_courses = Enrollment.objects.filter(is_completed=True).count()
    total_certificates = Certificate.objects.count()

    # Chart 1: Course Completion Status
    in_progress = total_enrollments - completed_courses
    completion_chart_data = {
        'labels': ['Completed', 'In Progress'],
        'data': [completed_courses, in_progress if in_progress >= 0 else 0]
    }

    # Chart 2: Popular Courses (Top 5)
    popular_courses = Course.objects.filter(status=Course.Status.PUBLISHED).annotate(
        enr_count=Count('enrollments')
    ).order_by('-enr_count')[:5]

    popular_chart_data = {
        'labels': [c.title[:25] + ('...' if len(c.title) > 25 else '') for c in popular_courses],
        'data': [c.enr_count for c in popular_courses]
    }

    # Chart 3: Department-wise Participation
    dept_participation = Department.objects.annotate(
        emp_count=Count('users', filter=Q(users__role=User.Role.EMPLOYEE))
    ).filter(emp_count__gt=0)[:6]

    dept_chart_data = {
        'labels': [d.code for d in dept_participation],
        'data': [d.emp_count for d in dept_participation]
    }

    # Chart 4: Competency Domain Breakdown
    domains_data = Competency.objects.values('domain').annotate(total=Count('id'))
    domain_labels = [d['domain'] for d in domains_data]
    domain_counts = [d['total'] for d in domains_data]
    competency_chart_data = {
        'labels': domain_labels if domain_labels else ['Scientific', 'Technical', 'Managerial', 'Operational'],
        'data': domain_counts if domain_counts else [5, 5, 3, 2]
    }

    # Tables Data
    pending_users = User.objects.filter(approval_status=User.ApprovalStatus.PENDING).order_by('-date_joined')[:5]
    recent_users = User.objects.select_related('department').order_by('-date_joined')[:6]
    recent_enrollments = Enrollment.objects.select_related('employee', 'course').order_by('-enrolled_at')[:6]

    return render(request, 'admin_dashboard/dashboard.html', {
        'total_users': total_users,
        'total_trainers': total_trainers,
        'total_employees': total_employees,
        'pending_approvals': pending_approvals,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'total_enrollments': total_enrollments,
        'completed_courses': completed_courses,
        'total_certificates': total_certificates,
        'completion_chart_json': json.dumps(completion_chart_data),
        'popular_chart_json': json.dumps(popular_chart_data),
        'dept_chart_json': json.dumps(dept_chart_data),
        'competency_chart_json': json.dumps(competency_chart_data),
        'pending_users': pending_users,
        'recent_users': recent_users,
        'recent_enrollments': recent_enrollments,
    })

@trainer_required
def trainer_dashboard_view(request):
    """Trainer-specific monitoring and performance workspace."""
    my_courses = Course.objects.filter(trainer=request.user)
    courses_count = my_courses.count()
    active_courses_count = my_courses.filter(status=Course.Status.PUBLISHED).count()

    my_enrollments = Enrollment.objects.filter(course__trainer=request.user).select_related('employee', 'course')
    total_enrollments = my_enrollments.count()
    completed_enrollments = my_enrollments.filter(is_completed=True).count()
    completion_rate = round((completed_enrollments / total_enrollments * 100), 1) if total_enrollments > 0 else 0.0

    # Assessment stats
    attempts = AssessmentAttempt.objects.filter(assessment__course__trainer=request.user)
    avg_score = attempts.aggregate(Avg('percentage_obtained'))['percentage_obtained__avg'] or 0.0

    # Feedbacks
    recent_feedbacks = CourseFeedback.objects.filter(course__trainer=request.user).select_related('employee', 'course')[:5]
    avg_rating = CourseFeedback.objects.filter(course__trainer=request.user).aggregate(Avg('trainer_rating'))['trainer_rating__avg'] or 0.0

    # Trainee progress table
    trainees = my_enrollments.order_by('-enrolled_at')[:10]

    return render(request, 'trainer/dashboard.html', {
        'courses_count': courses_count,
        'active_courses_count': active_courses_count,
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'completion_rate': completion_rate,
        'avg_score': round(avg_score, 1),
        'avg_rating': round(avg_rating, 1),
        'recent_feedbacks': recent_feedbacks,
        'trainees': trainees,
        'my_courses': my_courses[:5],
    })

@employee_required
def employee_dashboard_view(request):
    """Personalized learning and capacity building dashboard."""
    enrollments = Enrollment.objects.filter(employee=request.user).select_related('course', 'course__trainer').order_by('-enrolled_at')
    
    total_enrolled = enrollments.count()
    completed_count = enrollments.filter(is_completed=True).count()
    in_progress_count = total_enrolled - completed_count
    
    certificates = Certificate.objects.filter(enrollment__employee=request.user).select_related('enrollment__course')
    cert_count = certificates.count()

    # Recommended courses based on target skills
    target_skills = EmployeeCompetency.objects.filter(employee=request.user, is_target_skill=True).values_list('competency_id', flat=True)
    if target_skills:
        recommended_courses = Course.objects.filter(
            status=Course.Status.PUBLISHED,
            competency_outcomes__competency_id__in=target_skills
        ).exclude(enrollments__employee=request.user).distinct()[:4]
    else:
        recommended_courses = Course.objects.filter(
            status=Course.Status.PUBLISHED
        ).exclude(enrollments__employee=request.user)[:4]

    announcements = Announcement.objects.all()[:4]

    return render(request, 'employee/dashboard.html', {
        'enrollments': enrollments,
        'total_enrolled': total_enrolled,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'certificates': certificates,
        'cert_count': cert_count,
        'recommended_courses': recommended_courses,
        'announcements': announcements,
    })

@admin_required
def download_admin_report_view(request):
    """Generate and download executive PDF audit report."""
    pdf_buffer = generate_admin_report_pdf()
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    timestamp_str = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="Capacity_Connect_Audit_Report_{timestamp_str}.pdf"'
    return response

