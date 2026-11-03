from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import models
from .models import Announcement, Notification, CourseFeedback, TrainerResource
from .forms import AnnouncementForm, CourseFeedbackForm, TrainerResourceForm
from apps.courses.models import Course, Enrollment
from apps.accounts.decorators import admin_required, trainer_required, approval_required

def announcements_list_view(request):
    """View announcements list."""
    announcements = Announcement.objects.all()
    if not request.user.is_authenticated:
        announcements = announcements.filter(is_public=True)
    return render(request, 'communications/announcements.html', {'announcements': announcements})

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
def notification_list_view(request):
    """View user notifications."""
    notifications = request.user.notifications.all()
    # Mark all read on visit
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'communications/notifications.html', {'notifications': notifications})

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

    return render(request, 'communications/resource_library.html', {
        'resources': resources,
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

