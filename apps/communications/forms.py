from django import forms
from .models import Announcement, CourseFeedback, TrainerResource

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'announcement_type', 'content', 'is_public', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'announcement_type': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'content': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 4}),
            'is_public': forms.CheckboxInput(attrs={'class': 'rounded border-gov-300 text-brand-600 focus:ring-brand-500'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'rounded border-gov-300 text-brand-600 focus:ring-brand-500'}),
        }

class CourseFeedbackForm(forms.ModelForm):
    class Meta:
        model = CourseFeedback
        fields = ['course_rating', 'trainer_rating', 'comments', 'improvement_suggestions']
        widgets = {
            'course_rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)], attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'trainer_rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)], attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'comments': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3, 'placeholder': 'How effectively did this course build your capacity?'}),
            'improvement_suggestions': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2, 'placeholder': 'Suggestions for curriculum or delivery improvement'}),
        }

class TrainerResourceForm(forms.ModelForm):
    class Meta:
        model = TrainerResource
        fields = ['title', 'category', 'description', 'file', 'external_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'w-full text-sm text-gov-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100'}),
            'external_link': forms.URLInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': 'https://...'}),
        }

