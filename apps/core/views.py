from django.shortcuts import redirect, render
from django.db.models import Count
from apps.courses.models import Course, Category, Enrollment
from apps.competencies.models import Competency
from apps.communications.models import Announcement
from django.contrib.auth import get_user_model

User = get_user_model()

def landing_view(request):
    """Public portal landing page."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    featured_courses = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('trainer', 'category').annotate(
        enrolled_count=Count('enrollments')
    ).order_by('-enrolled_count')[:6]

    categories = Category.objects.annotate(course_count=Count('courses')).filter(course_count__gt=0)[:8]
    if not categories.exists():
        categories = Category.objects.all()[:8]

    announcements = Announcement.objects.filter(is_public=True).order_by('-is_pinned', '-created_at')[:4]
    
    # Real metrics
    total_courses = Course.objects.filter(status=Course.Status.PUBLISHED).count()
    total_learners = User.objects.filter(role=User.Role.EMPLOYEE, approval_status=User.ApprovalStatus.APPROVED).count()
    total_competencies = Competency.objects.count()
    total_completions = Enrollment.objects.filter(is_completed=True).count()

    return render(request, 'public/landing.html', {
        'featured_courses': featured_courses,
        'categories': categories,
        'announcements': announcements,
        'total_courses': total_courses,
        'total_learners': total_learners,
        'total_competencies': total_competencies,
        'total_completions': total_completions,
    })

def about_view(request):
    """About Capacity Connect & SIH26075 vision."""
    return render(request, 'public/about.html')

# Custom Error Views
def bad_request_view(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def permission_denied_view(request, exception=None):
    return render(request, 'errors/403.html', {'exception': exception}, status=403)

def page_not_found_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def server_error_view(request):
    return render(request, 'errors/500.html', status=500)

