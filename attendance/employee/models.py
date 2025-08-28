from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

# Create your models here.

class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('hr_admin', 'HR/Admin'),  # Changed from 'hr' to avoid conflict
        ('staff', 'Staff'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('human_resources', 'Human Resources'),  # Changed from 'hr' to avoid conflict
        ('information_technology', 'Information Technology'),
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('marketing', 'Marketing'),
        ('operations', 'Operations'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES)  # Increased max_length
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.employee_id}"
    
    def clean(self):
        """Model validation"""
        # Validate hire date is not in the future
        if self.hire_date and self.hire_date > date.today():
            raise ValidationError({'hire_date': 'Hire date cannot be in the future.'})
        
        # Validate employee ID format (EMP + 3 digits)
        if self.employee_id and not self.employee_id.startswith('EMP'):
            raise ValidationError({'employee_id': 'Employee ID must start with "EMP".'})
    
    def get_full_name(self):
        """Get employee's full name with fallback"""
        full_name = self.user.get_full_name()
        return full_name if full_name.strip() else self.user.username
    
    def can_manage_attendance(self):
        """Check if employee can manage attendance for others"""
        return self.role in ['manager', 'hr_admin']
    
    def can_view_salary_info(self):
        """Check if employee can view salary information"""
        return self.role in ['hr_admin']
    
    def is_in_management(self):
        """Check if employee is in management position"""
        return self.role in ['manager', 'hr_admin']
    
    def get_department_display_name(self):
        """Get human-readable department name"""
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)
    
    def get_role_display_name(self):
        """Get human-readable role name"""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
    
    @property
    def years_of_service(self):
        """Calculate years of service"""
        if self.hire_date:
            today = date.today()
            return (today - self.hire_date).days / 365.25
        return 0
    
    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
