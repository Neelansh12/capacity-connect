from django import forms
from .models import Competency, TrainerCompetency, EmployeeCompetency, Proficiency

class CompetencyForm(forms.ModelForm):
    class Meta:
        model = Competency
        fields = ['name', 'domain', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'domain': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3}),
        }

class TrainerCompetencyForm(forms.ModelForm):
    class Meta:
        model = TrainerCompetency
        fields = ['competency', 'proficiency_level', 'experience_years', 'supporting_description']
        widgets = {
            'competency': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'proficiency_level': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'supporting_description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2, 'placeholder': 'Key projects, research, or training delivered'}),
        }

class EmployeeCompetencyForm(forms.ModelForm):
    class Meta:
        model = EmployeeCompetency
        fields = ['competency', 'proficiency_level', 'is_target_skill']
        widgets = {
            'competency': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'proficiency_level': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'is_target_skill': forms.CheckboxInput(attrs={'class': 'rounded border-gov-300 text-brand-600 focus:ring-brand-500'}),
        }

