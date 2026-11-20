from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from .models import Course, CourseModule, LearningResource, Enrollment, ModuleProgress, Category
from .forms import CourseForm, CourseModuleForm, LearningResourceForm
from apps.accounts.decorators import approval_required, trainer_required

def course_catalog_view(request):
    """Public and authenticated course catalog with filters."""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')

    courses = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('trainer', 'category')

    if query:
        courses = courses.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(trainer__first_name__icontains=query) |
            models.Q(trainer__last_name__icontains=query)
        )
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if difficulty:
        courses = courses.filter(difficulty_level=difficulty)

    categories = Category.objects.all()

    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Track enrolled course IDs for authenticated users
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = list(Enrollment.objects.filter(employee=request.user).values_list('course_id', flat=True))

    return render(request, 'courses/catalog.html', {
        'courses': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'search_query': query,
        'enrolled_course_ids': enrolled_course_ids,
    })

def course_detail_view(request, slug):
    """Course detail page."""
    course = get_object_or_404(Course.objects.select_related('trainer', 'category').prefetch_related('modules__resources'), slug=slug)

    # If course is draft or archived, only author or admin can view
    if course.status != Course.Status.PUBLISHED:
        if not (request.user.is_authenticated and (request.user == course.trainer or request.user.is_admin_role())):
            raise PermissionDenied("This course is currently in draft mode.")

    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(employee=request.user, course=course).first()

    return render(request, 'courses/detail.html', {
        'course': course,
        'enrollment': enrollment,
    })

@login_required
@approval_required
def course_enroll_view(request, slug):
    """Enroll employee in a course."""
    if request.method != 'POST':
        return redirect('courses:detail', slug=slug)

    course = get_object_or_404(Course, slug=slug, status=Course.Status.PUBLISHED)

    # Check for existing enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        employee=request.user,
        course=course,
        defaults={'progress_percentage': 0.0}
    )

    if created:
        # Initialize ModuleProgress for each module in course
        modules = course.modules.all()
        for module in modules:
            ModuleProgress.objects.get_or_create(enrollment=enrollment, module=module)
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, "You are already enrolled in this course.")

    return redirect('courses:learn', slug=course.slug)

# Alias matching Project Report Specification (Page 13)
enroll_view = course_enroll_view

@login_required
@approval_required
def course_learn_view(request, slug):
    """Interactive learning portal for enrolled employees."""
    course = get_object_or_404(Course, slug=slug)
    
    # Check enrollment or ownership
    is_author = (request.user == course.trainer or request.user.is_admin_role())
    enrollment = Enrollment.objects.filter(employee=request.user, course=course).first()

    if not enrollment and not is_author:
        messages.error(request, "Please enroll in the course to access learning materials.")
        return redirect('courses:detail', slug=slug)

    modules = course.modules.prefetch_related('resources').order_by('order')
    
    # Selected module
    module_id = request.GET.get('module')
    if module_id:
        current_module = modules.filter(id=module_id).first() or modules.first()
    else:
        current_module = modules.first()

    # Progress mapping
    completed_module_ids = set()
    if enrollment:
        completed_module_ids = set(
            ModuleProgress.objects.filter(enrollment=enrollment, is_completed=True).values_list('module_id', flat=True)
        )

    # Check if assessment is available
    assessment = getattr(course, 'assessment', None)

    return render(request, 'courses/learn.html', {
        'course': course,
        'modules': modules,
        'current_module': current_module,
        'enrollment': enrollment,
        'completed_module_ids': completed_module_ids,
        'assessment': assessment,
        'is_author': is_author,
    })

# Alias matching Project Report Specification (Page 13)
learn_view = course_learn_view

@login_required
@approval_required
def module_complete_view(request, module_id):
    """Mark a module complete and recalculate genuine course progress."""
    if request.method != 'POST':
        return redirect('accounts:dashboard_redirect')

    module = get_object_or_404(CourseModule, id=module_id)
    enrollment = get_object_or_404(Enrollment, employee=request.user, course=module.course)

    mod_progress, _ = ModuleProgress.objects.get_or_create(enrollment=enrollment, module=module)
    mod_progress.mark_as_completed()

    messages.success(request, f"Module '{module.title}' marked as completed! Overall progress updated.")
    return redirect(f"/courses/{module.course.slug}/learn/?module={module.id}")

# Trainer Course Management
@trainer_required
def trainer_course_list_view(request):
    """List courses created by the trainer (or all if admin)."""
    if request.user.is_admin_role():
        courses = Course.objects.all().select_related('trainer', 'category').annotate(
            enrolled_count=models.Count('enrollments')
        ).order_by('-created_at')
    else:
        courses = Course.objects.filter(trainer=request.user).select_related('category').annotate(
            enrolled_count=models.Count('enrollments')
        ).order_by('-created_at')

    return render(request, 'trainer/course_list.html', {'courses': courses})

@trainer_required
def trainer_course_create_view(request):
    """Create a new course."""
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.trainer = request.user
            course.save()
            messages.success(request, f"Course '{course.title}' created successfully! Now add learning modules.")
            return redirect('courses:manage_modules', course_id=course.id)
    else:
        form = CourseForm()

    return render(request, 'trainer/course_form.html', {'form': form, 'title': 'Create New Course'})

@trainer_required
def trainer_course_edit_view(request, course_id):
    """Edit existing course with ownership authorization."""
    course = get_object_or_404(Course, id=course_id)
    if course.trainer != request.user and not request.user.is_admin_role():
        raise PermissionDenied("You do not have permission to edit another trainer's course.")

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully.")
            return redirect('courses:trainer_course_list')
    else:
        form = CourseForm(instance=course)

    return render(request, 'trainer/course_form.html', {'form': form, 'course': course, 'title': f'Edit Course: {course.title}'})

@trainer_required
def trainer_module_manage_view(request, course_id):
    """Manage modules for a course."""
    course = get_object_or_404(Course, id=course_id)
    if course.trainer != request.user and not request.user.is_admin_role():
        raise PermissionDenied("You do not have permission to manage this course.")

    if request.method == 'POST':
        form = CourseModuleForm(request.POST)
        if form.is_valid():
            mod = form.save(commit=False)
            mod.course = course
            mod.save()
            messages.success(request, f"Module '{mod.title}' added.")
            return redirect('courses:manage_modules', course_id=course.id)
    else:
        next_order = course.modules.count() + 1
        form = CourseModuleForm(initial={'order': next_order})

    modules = course.modules.prefetch_related('resources').order_by('order')
    return render(request, 'trainer/module_manage.html', {
        'course': course,
        'modules': modules,
        'form': form,
    })

@trainer_required
def trainer_resource_manage_view(request, module_id):
    """Add learning resource to a module."""
    module = get_object_or_404(CourseModule, id=module_id)
    if module.course.trainer != request.user and not request.user.is_admin_role():
        raise PermissionDenied("You do not have permission to manage this module.")

    if request.method == 'POST':
        form = LearningResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.module = module
            resource.save()
            messages.success(request, f"Resource '{resource.title}' uploaded successfully.")
            return redirect('courses:manage_modules', course_id=module.course.id)
    else:
        next_order = module.resources.count() + 1
        form = LearningResourceForm(initial={'order': next_order})

    return render(request, 'trainer/resource_form.html', {
        'module': module,
        'course': module.course,
        'form': form,
    })

