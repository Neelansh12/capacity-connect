from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import models
from .models import Announcement, Notification, CourseFeedback, TrainerResource
from .forms import AnnouncementForm, CourseFeedbackForm, TrainerResourceForm
from apps.courses.models import Course, Enrollment
from apps.accounts.decorators import admin_required, trainer_required, approval_required

def announcements_view(request):
    """View announcements list (name matched to Project Report Specification)."""
    announcements = Announcement.objects.all()
    if not request.user.is_authenticated:
        announcements = announcements.filter(is_public=True)
    return render(request, 'communications/announcements.html', {'announcements': announcements})

# Backward compatibility alias
announcements_list_view = announcements_view

@admin_required
def announcement_create_view(request):
    """Admin publish announcement."""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            messages.success(request, "Announcement published successfully.")
            return redirect('communications:announcements')
    else:
        form = AnnouncementForm()
    return render(request, 'communications/announcement_form.html', {'form': form})

@login_required
def notifications_view(request):
    """View user notifications (name matched to Project Report Specification)."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            request.user.notifications.filter(is_read=False).update(is_read=True)
            messages.success(request, "All notifications marked as read.")
            return redirect('communications:notifications')
        elif action == 'mark_read':
            notif_id = request.POST.get('notification_id')
            if notif_id:
                request.user.notifications.filter(id=notif_id).update(is_read=True)
                return redirect('communications:notifications')

    notifications = request.user.notifications.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'communications/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

# Backward compatibility alias
notification_list_view = notifications_view

@login_required
def notification_unread_api_view(request):
    """
    Real-Time Notification API endpoint (achieves the dynamic notifications claimed in report).
    Returns real-time unread counts and recent alerts for the live navbar poller.
    """
    unread_qs = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
    count = request.user.notifications.filter(is_read=False).count()
    data = {
        'unread_count': count,
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'created_at': n.created_at.strftime('%d %b, %H:%M'),
                'notification_type': n.notification_type,
                'target_url': n.target_url or '',
            }
            for n in unread_qs
        ]
    }
    return JsonResponse(data)

@login_required
def mark_notification_read_api_view(request, notification_id):
    """API endpoint to mark single notification as read via POST."""
    if request.method == 'POST':
        notif = get_object_or_404(request.user.notifications, id=notification_id)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'POST required'}, status=405)

@login_required
@approval_required
def course_feedback_view(request, slug):
    """Submit course & trainer feedback."""
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, employee=request.user, course=course)

    feedback = CourseFeedback.objects.filter(course=course, employee=request.user).first()

    if request.method == 'POST':
        form = CourseFeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.course = course
            fb.employee = request.user
            fb.save()
            messages.success(request, "Thank you for your valuable feedback! It assists in continuous curriculum enhancement.")
            return redirect('courses:learn', slug=course.slug)
    else:
        form = CourseFeedbackForm(instance=feedback)

    return render(request, 'courses/feedback.html', {
        'course': course,
        'form': form,
        'feedback': feedback,
    })

def resource_library_view(request):
    """Centralized Knowledge & Resource Library."""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')

    resources = TrainerResource.objects.select_related('uploaded_by').all()

    if query:
        resources = resources.filter(
            models.Q(title__icontains=query) | models.Q(description__icontains=query)
        )
    if category:
        resources = resources.filter(category=category)

    paginator = Paginator(resources, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'communications/resource_library.html', {
        'resources': page_obj,
        'page_obj': page_obj,
        'categories': TrainerResource.Category.choices,
        'selected_category': category,
        'search_query': query,
    })

@trainer_required
def resource_upload_view(request):
    """Upload material to Centralized Knowledge Library."""
    if request.method == 'POST':
        form = TrainerResourceForm(request.POST, request.FILES)
        if form.is_valid():
            res = form.save(commit=False)
            res.uploaded_by = request.user
            res.save()
            messages.success(request, f"Resource '{res.title}' added to Knowledge Library.")
            return redirect('communications:resource_library')
    else:
        form = TrainerResourceForm()
    return render(request, 'communications/resource_upload.html', {'form': form})

