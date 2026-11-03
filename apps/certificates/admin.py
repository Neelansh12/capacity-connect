from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'get_employee', 'get_course', 'issued_at')
    search_fields = ('certificate_id', 'verification_code', 'enrollment__employee__username', 'enrollment__course__title')
    readonly_fields = ('certificate_id', 'verification_code', 'issued_at')

    def get_employee(self, obj):
        return obj.enrollment.employee.username
    get_employee.short_description = 'Employee'

    def get_course(self, obj):
        return obj.enrollment.course.title
    get_course.short_description = 'Course'

