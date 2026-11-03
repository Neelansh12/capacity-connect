from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def approval_required(view_func):
    """Ensure the user is authenticated and approved by admin."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_approved():
            return redirect('accounts:pending_approval')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """Requires user to be an Administrator."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_approved():
            return redirect('accounts:pending_approval')
        if not request.user.is_admin_role():
            messages.error(request, "Access restricted to Administrators only.")
            raise PermissionDenied("Administrator privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def trainer_required(view_func):
    """Requires user to be a Trainer or Admin."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_approved():
            return redirect('accounts:pending_approval')
        if not (request.user.is_trainer_role() or request.user.is_admin_role()):
            messages.error(request, "Access restricted to Trainers and Instructors.")
            raise PermissionDenied("Trainer privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def employee_required(view_func):
    """Requires user to be an Employee or Admin."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_approved():
            return redirect('accounts:pending_approval')
        if not (request.user.is_employee_role() or request.user.is_admin_role()):
            messages.error(request, "Access restricted to Employees.")
            raise PermissionDenied("Employee privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

