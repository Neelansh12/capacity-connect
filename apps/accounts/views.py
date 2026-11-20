from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import User, EmployeeProfile, TrainerProfile, Department, Designation
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    EmployeeProfileForm, 
    TrainerProfileForm, 
    AdminUserApprovalForm
)
from .decorators import admin_required, approval_required

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)

            # Document Bootstrap Specification: The first user to register becomes ADMIN and superuser
            is_first_user = (User.objects.count() == 0)
            if is_first_user:
                user.role = User.Role.ADMIN
                user.approval_status = User.ApprovalStatus.APPROVED
                user.is_staff = True
                user.is_superuser = True
                user.approved_at = timezone.now()
            else:
                user.approval_status = User.ApprovalStatus.PENDING
                user.is_staff = False
                user.is_superuser = False
                user.approved_at = None

            user.save()

            # Create corresponding profile
            if user.role == User.Role.EMPLOYEE:
                EmployeeProfile.objects.create(
                    user=user, 
                    employee_id=form.cleaned_data.get('employee_id') or f"EMP-{user.id:04d}"
                )
            elif user.role == User.Role.TRAINER:
                TrainerProfile.objects.create(user=user)

            if is_first_user:
                messages.success(
                    request,
                    "System initialized! First user registered and bootstrapped as Administrator with full privileges."
                )
            else:
                messages.success(
                    request, 
                    "Registration successful! Your account is pending administrative approval."
                )
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Try login by username, if fails try by email
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account has been deactivated. Contact an administrator.")
                else:
                    login(request, user)
                    if not user.is_approved():
                        return redirect('accounts:pending_approval')
                    messages.success(request, f"Welcome back, {user.get_full_name_or_username()}!")
                    return redirect('accounts:dashboard_redirect')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('accounts:login')

@login_required
def pending_approval_view(request):
    if request.user.is_approved():
        return redirect('accounts:dashboard_redirect')
    return render(request, 'registration/pending_approval.html', {'user': request.user})

@login_required
def dashboard_redirect_view(request):
    if not request.user.is_approved():
        return redirect('accounts:pending_approval')

    if request.user.is_admin_role():
        return redirect('analytics:admin_dashboard')
    elif request.user.is_trainer_role():
        return redirect('analytics:trainer_dashboard')
    else:
        return redirect('analytics:employee_dashboard')

@login_required
@approval_required
def profile_view(request):
    user = request.user
    profile = None

    if user.is_employee_role() or user.is_admin_role():
        profile, _ = EmployeeProfile.objects.get_or_create(user=user)
        FormClass = EmployeeProfileForm
    else:
        profile, _ = TrainerProfile.objects.get_or_create(user=user)
        FormClass = TrainerProfileForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User fields from form
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.email = form.cleaned_data.get('email', user.email)
            user.phone_number = form.cleaned_data.get('phone_number', user.phone_number)
            if 'department' in form.cleaned_data:
                user.department = form.cleaned_data['department']
            if 'designation' in form.cleaned_data:
                user.designation = form.cleaned_data['designation']
            user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'department': user.department,
            'designation': user.designation,
        }
        form = FormClass(instance=profile, initial=initial)

    return render(request, 'registration/profile.html', {
        'form': form,
        'profile': profile,
    })

# Admin User Management Views
@admin_required
def admin_user_list_view(request):
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    dept_filter = request.GET.get('department', '')
    search_query = request.GET.get('q', '').strip()

    users = User.objects.all().select_related('department', 'designation').order_by('-date_joined')

    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter:
        users = users.filter(approval_status=status_filter)
    if dept_filter:
        users = users.filter(department_id=dept_filter)
    if search_query:
        users = users.filter(
            models.Q(username__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )

    departments = Department.objects.all()

    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/user_list.html', {
        'users': page_obj,
        'page_obj': page_obj,
        'departments': departments,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'search_query': search_query,
    })

@admin_required
def admin_user_approval_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('rejection_reason', '').strip()

        if action == 'approve':
            target_user.approval_status = User.ApprovalStatus.APPROVED
            target_user.approved_at = timezone.now()
            target_user.save()
            messages.success(request, f"User {target_user.username} has been approved.")
        elif action == 'reject':
            target_user.approval_status = User.ApprovalStatus.REJECTED
            target_user.rejection_reason = reason
            target_user.save()
            messages.warning(request, f"User {target_user.username} was rejected.")
        elif action == 'toggle_active':
            target_user.is_active = not target_user.is_active
            target_user.save()
            status_text = "activated" if target_user.is_active else "deactivated"
            messages.info(request, f"User {target_user.username} was {status_text}.")

    return redirect('accounts:admin_user_list')

