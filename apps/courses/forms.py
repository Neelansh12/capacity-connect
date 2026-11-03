from django import forms
from .models import Course, CourseModule, LearningResource, Category

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'category', 'difficulty_level', 'estimated_duration_hours',
            'description', 'learning_objectives', 'prerequisites', 'thumbnail', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': 'e.g. Advanced Meteorological Data Analysis'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'difficulty_level': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'estimated_duration_hours': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 4}),
            'learning_objectives': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3, 'placeholder': 'What learners will achieve upon completion'}),
            'prerequisites': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2, 'placeholder': 'Prerequisite skills or previous courses'}),
            'status': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
        }

class CourseModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        fields = ['title', 'description', 'order', 'is_mandatory']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': 'Module Title'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'rounded border-gov-300 text-brand-600 focus:ring-brand-500'}),
        }

class LearningResourceForm(forms.ModelForm):
    class Meta:
        model = LearningResource
        fields = ['title', 'resource_type', 'file', 'external_url', 'text_content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'resource_type': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'file': forms.FileInput(attrs={'class': 'w-full text-sm text-gov-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100'}),
            'external_url': forms.URLInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': 'https://...'}),
            'text_content': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
        }

