from django.contrib import admin
from .models import Assessment, Question, AnswerOption, AssessmentAttempt, SubmittedAnswer

class OptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_percentage', 'duration_minutes', 'max_attempts', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'course__title')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'assessment', 'marks', 'order')
    list_filter = ('assessment',)
    inlines = [OptionInline]

@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('employee', 'assessment', 'attempt_number', 'score_obtained', 'total_marks', 'percentage_obtained', 'passed', 'submitted_at')
    list_filter = ('passed', 'assessment')
    search_fields = ('employee__username', 'assessment__title')

@admin.register(SubmittedAnswer)
class SubmittedAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct')
    list_filter = ('is_correct',)

