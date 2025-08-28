from django.shortcuts import redirect
from django.contrib import messages
from .models import Employee

def hr_admin_required(view_func):
    """Decorator to ensure only HR/Admin can access the view"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        
        try:
            employee = request.user.employee_profile
            if not employee.can_manage_attendance():
                messages.error(request, "You don't have permission to manage employees.")
                return redirect('dashboard')
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found.")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper