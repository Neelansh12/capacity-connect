from django import forms
from .models import Assessment, Question, AnswerOption

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = [
            'title', 'description', 'passing_percentage', 'duration_minutes', 
            'max_attempts', 'start_date', 'end_date', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3}),
            'passing_percentage': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'max_attempts': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'type': 'datetime-local'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'rounded border-gov-300 text-brand-600 focus:ring-brand-500'}),
        }

class QuestionForm(forms.ModelForm):
    option_1 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    option_2 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    option_3 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    option_4 = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    correct_option = forms.ChoiceField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        widget=forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'})
    )

    class Meta:
        model = Question
        fields = ['question_text', 'marks', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2}),
            'marks': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'order': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
        }

