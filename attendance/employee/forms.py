from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Employee

class EmployeeForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'phone_number', 'address', 'department', 
            'role', 'hire_date', 'salary', 'is_active'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        # If editing existing employee, populate user fields
        if self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username
    
    def clean_username(self):
        username = self.cleaned_data['username']
        user_qs = User.objects.filter(username=username)
        
        # If editing, exclude current user from uniqueness check
        if self.instance.pk and self.instance.user:
            user_qs = user_qs.exclude(pk=self.instance.user.pk)
        
        if user_qs.exists():
            raise ValidationError("A user with this username already exists.")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        user_qs = User.objects.filter(email=email)
        
        # If editing, exclude current user from uniqueness check
        if self.instance.pk and self.instance.user:
            user_qs = user_qs.exclude(pk=self.instance.user.pk)
        
        if user_qs.exists():
            raise ValidationError("A user with this email already exists.")
        
        return email
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        
        # Check uniqueness
        employee_qs = Employee.objects.filter(employee_id=employee_id)
        if self.instance.pk:
            employee_qs = employee_qs.exclude(pk=self.instance.pk)
        
        if employee_qs.exists():
            raise ValidationError("An employee with this ID already exists.")
        
        return employee_id
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        
        # Create or update User instance
        if employee.pk and employee.user:
            # Updating existing employee
            user = employee.user
        else:
            # Creating new employee
            user = User()
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        
        if commit:
            user.save()
            employee.user = user
            employee.save()
        
        return employee

class EmployeeSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, employee ID, or email...',
            'class': 'form-control'
        })
    )
    department = forms.ChoiceField(
        choices=[('', 'All Departments')] + Employee.DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=[('', 'All Roles')] + Employee.ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Active'), ('false', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class EmployeeProfileForm(forms.ModelForm):
    """Form for employees to edit their own profile information"""
    # User fields that employees can edit
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = Employee
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing employee, populate user fields
        if self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def clean_email(self):
        email = self.cleaned_data['email']
        user_qs = User.objects.filter(email=email)
        
        # If editing, exclude current user from uniqueness check
        if self.instance.pk and self.instance.user:
            user_qs = user_qs.exclude(pk=self.instance.user.pk)
        
        if user_qs.exists():
            raise ValidationError("A user with this email already exists.")
        
        return email
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        
        # Update User instance
        if employee.user:
            user = employee.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            
            if commit:
                user.save()
                employee.save()
        
        return employee
