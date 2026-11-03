from django.contrib import admin
from .models import Competency, TrainerCompetency, EmployeeCompetency, CourseCompetency

@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'slug', 'created_at')
    list_filter = ('domain',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(TrainerCompetency)
class TrainerCompetencyAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'competency', 'proficiency_level', 'experience_years', 'created_at')
    list_filter = ('proficiency_level', 'competency__domain')
    search_fields = ('trainer__username', 'competency__name')

@admin.register(EmployeeCompetency)
class EmployeeCompetencyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'competency', 'proficiency_level', 'is_target_skill', 'created_at')
    list_filter = ('is_target_skill', 'proficiency_level')
    search_fields = ('employee__username', 'competency__name')

@admin.register(CourseCompetency)
class CourseCompetencyAdmin(admin.ModelAdmin):
    list_display = ('course', 'competency', 'target_proficiency')
    list_filter = ('target_proficiency',)

