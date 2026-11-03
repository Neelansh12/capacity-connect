from django.contrib import admin
from .models import Category, Course, CourseModule, LearningResource, Enrollment, ModuleProgress

class ModuleInline(admin.StackedInline):
    model = CourseModule
    extra = 1

class ResourceInline(admin.StackedInline):
    model = LearningResource
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_name', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'category', 'difficulty_level', 'status', 'created_at')
    list_filter = ('status', 'difficulty_level', 'category')
    search_fields = ('title', 'description', 'trainer__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_mandatory')
    list_filter = ('course', 'is_mandatory')
    inlines = [ResourceInline]

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'resource_type', 'order')
    list_filter = ('resource_type',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'course', 'progress_percentage', 'is_completed', 'enrolled_at')
    list_filter = ('is_completed', 'course')
    search_fields = ('employee__username', 'course__title')

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'module', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)

