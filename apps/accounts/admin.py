from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Designation, EmployeeProfile, TrainerProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'approval_status', 'is_active', 'department')
    list_filter = ('role', 'approval_status', 'is_active', 'department')
    fieldsets = UserAdmin.fieldsets + (
        ('Capacity Connect Details', {
            'fields': ('role', 'approval_status', 'phone_number', 'department', 'designation', 'rejection_reason', 'approved_at')
        }),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'level', 'created_at')
    list_filter = ('department', 'level')
    search_fields = ('title',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'experience_years', 'created_at')
    search_fields = ('user__username', 'employee_id')

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'created_at')
    search_fields = ('user__username',)

