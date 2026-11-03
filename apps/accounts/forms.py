from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, EmployeeProfile, TrainerProfile, Department, Designation

class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        (User.Role.EMPLOYEE, 'Employee / Learner'),
        (User.Role.TRAINER, 'Trainer / Instructor'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'})
    )
    employee_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': 'e.g. MOES-EMP-2026-042'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'department', 'designation', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'department': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'designation': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
        }

    def clean_role(self):
        role = self.cleaned_data.get('role')
        # Security: never allow self-registration as ADMIN
        if role not in [User.Role.EMPLOYEE, User.Role.TRAINER]:
            raise forms.ValidationError("Invalid role selected for self-registration.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'placeholder': '••••••••'})
    )

class EmployeeProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, widget=forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    designation = forms.ModelChoiceField(queryset=Designation.objects.all(), required=False, widget=forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))

    class Meta:
        model = EmployeeProfile
        fields = ['employee_id', 'qualifications', 'experience_years', 'areas_of_interest', 'learning_objectives', 'avatar']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'qualifications': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'areas_of_interest': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2}),
            'learning_objectives': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2}),
        }

class TrainerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, widget=forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))
    designation = forms.ModelChoiceField(queryset=Designation.objects.all(), required=False, widget=forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}))

    class Meta:
        model = TrainerProfile
        fields = ['qualifications', 'experience_years', 'areas_of_expertise', 'biography', 'avatar']
        widgets = {
            'qualifications': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'areas_of_expertise': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2}),
            'biography': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 3}),
        }

class AdminUserApprovalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['approval_status', 'role', 'rejection_reason', 'is_active']
        widgets = {
            'approval_status': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'role': forms.Select(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gov-300 shadow-sm focus:border-brand-500 focus:ring-brand-500', 'rows': 2}),
        }

