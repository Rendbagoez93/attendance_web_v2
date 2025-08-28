from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employee.models import Employee
from .models import Attendance
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from datetime import time, date, datetime
import json
from functools import wraps

# Create your views here.

# Utility functions and decorators
def get_employee_or_none(user):
    """Get employee instance or return None"""
    try:
        return Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return None

def get_today_attendance(employee, today=None):
    """Get today's attendance record for an employee"""
    if today is None:
        today = timezone.localtime().date()
    try:
        return Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        return None

def create_json_response(success, message, response_type, **kwargs):
    """Create standardized JSON response"""
    response = {
        'success': success,
        'message': message,
        'type': response_type
    }
    response.update(kwargs)
    return JsonResponse(response)

def get_today_attendance_stats(today=None):
    """Get attendance statistics for today"""
    if today is None:
        today = timezone.localtime().date()
    
    today_attendance = Attendance.objects.filter(date=today)
    present_count = today_attendance.filter(status__in=['present', 'late']).count()
    late_count = today_attendance.filter(is_late=True).count()
    
    return {
        'today_attendance': today_attendance,
        'present_count': present_count,
        'late_count': late_count,
        'today': today
    }

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            employee = get_employee_or_none(request.user)
            if not employee:
                messages.error(request, 'Employee profile not found.')
                return redirect('login')
            
            if employee.role not in allowed_roles:
                return HttpResponseForbidden(f"Access denied. {'/'.join(allowed_roles).title()} access required.")
            
            return view_func(request, employee, *args, **kwargs)
        return wrapper
    return decorator

def is_valid_check_in_time(current_time):
    """Check if current time is valid for check-in"""
    return time(8, 0) <= current_time <= time(9, 15)

def is_valid_check_out_time(current_time):
    """Check if current time is valid for check-out"""
    return current_time >= time(17, 0)

def determine_late_status(check_in_time):
    """Determine if check-in time is late"""
    return check_in_time > time(9, 15)

def calculate_work_duration(check_in_time, check_out_time, date_obj):
    """Calculate work duration in hours"""
    return (datetime.combine(date_obj, check_out_time) - 
            datetime.combine(date_obj, check_in_time)).total_seconds() / 3600

def user_login(request):
    """Login view with role-based redirection"""
    # Check if user is already logged in
    if request.user.is_authenticated:
        # Only redirect to dashboard if it's a POST request (actual login)
        # For GET requests, show login page so user can switch accounts if needed
        if request.method == 'POST':
            return redirect('dashboard')
        else:
            # User is logged in but accessing login page directly
            # Give them option to continue to dashboard or logout
            messages.info(request, f'You are already logged in as {request.user.username}. You can continue to dashboard or logout to switch accounts.')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Please contact an administrator.')
                return render(request, 'emp_attd/login.html')
            
            login(request, user)
            
            # Get employee info for detailed welcome message
            try:
                employee = Employee.objects.get(user=user)
                welcome_msg = f'Welcome back, {user.get_full_name() or user.username}! '
                welcome_msg += f'You are logged in as {employee.get_role_display()} in {employee.get_department_display()}.'
                messages.success(request, welcome_msg)
            except Employee.DoesNotExist:
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please check your credentials and try again.')
    
    return render(request, 'emp_attd/login.html')

def user_logout(request):
    """Logout view with confirmation"""
    user_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else 'User'
    logout(request)
    messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    """Main dashboard that redirects based on user role"""
    employee = get_employee_or_none(request.user)
    if not employee:
        messages.error(request, 'Employee profile not found. Please contact administrator.')
        return redirect('login')
    
    role_redirects = {
        'manager': 'manager_dashboard',
        'hr_admin': 'hr_dashboard',  # Updated from 'hr' to 'hr_admin'
        'staff': 'employee_dashboard'
    }
    
    if employee.role in role_redirects:
        return redirect(role_redirects[employee.role])
    else:
        messages.error(request, 'Unknown role. Please contact administrator.')
        return redirect('login')

@login_required
@role_required(['manager'])
def manager_dashboard(request, employee):
    """Manager dashboard view"""
    # Get all employees for manager overview
    all_employees = Employee.objects.all().order_by('employee_id')
    staff_count = Employee.objects.filter(role='staff').count()
    hr_count = Employee.objects.filter(role='hr_admin').count()  # Updated to hr_admin
    
    # Get today's attendance data
    attendance_stats = get_today_attendance_stats()
    employee_attendance = get_today_attendance(employee, attendance_stats['today'])
    
    context = {
        'employee': employee,
        'all_employees': all_employees,
        'staff_count': staff_count,
        'hr_count': hr_count,
        'total_employees': all_employees.count(),
        'present_count': attendance_stats['present_count'],
        'late_count': attendance_stats['late_count'],
        'employee_attendance': employee_attendance,
        'current_time': timezone.localtime(),
    }
    return render(request, 'emp_attd/manager_dashboard.html', context)

@login_required
@role_required(['hr_admin'])
def hr_dashboard(request, employee):
    """HR/Admin dashboard view"""
    # Get employee statistics for HR
    all_employees = Employee.objects.all().order_by('employee_id')
    departments = Employee.objects.values_list('department', flat=True).distinct()
    
    # Department-wise employee count
    dept_stats = {}
    for dept in departments:
        dept_display = dict(Employee.DEPARTMENT_CHOICES).get(dept, dept)
        dept_stats[dept_display] = Employee.objects.filter(department=dept).count()
    
    # Get today's attendance data
    attendance_stats = get_today_attendance_stats()
    absent_count = all_employees.count() - attendance_stats['present_count']
    employee_attendance = get_today_attendance(employee, attendance_stats['today'])
    
    context = {
        'employee': employee,
        'all_employees': all_employees,
        'total_employees': all_employees.count(),
        'active_employees': Employee.objects.filter(is_active=True).count(),
        'dept_stats': dept_stats,
        'present_count': attendance_stats['present_count'],
        'late_count': attendance_stats['late_count'],
        'absent_count': absent_count,
        'employee_attendance': employee_attendance,
        'current_time': timezone.localtime(),
    }
    return render(request, 'emp_attd/hr_dashboard.html', context)

@login_required
@role_required(['staff'])
def employee_dashboard(request, employee):
    """Staff employee dashboard view"""
    # Get employee's own information and department colleagues
    colleagues = Employee.objects.filter(
        department=employee.department
    ).exclude(user=request.user).order_by('employee_id')
    
    # Get today's attendance
    today = timezone.localtime().date()
    employee_attendance = get_today_attendance(employee, today)
    
    context = {
        'employee': employee,
        'colleagues': colleagues,
        'department_name': employee.get_department_display_name(),  # Use new method
        'employee_attendance': employee_attendance,
        'current_time': timezone.localtime(),
    }
    return render(request, 'emp_attd/employee_dashboard.html', context)

@login_required
def check_in(request):
    """Handle check-in functionality"""
    if request.method != 'POST':
        return create_json_response(False, 'Invalid request method', 'error')
    
    employee = get_employee_or_none(request.user)
    if not employee:
        return create_json_response(False, 'Employee profile not found', 'error')
    
    today = timezone.localtime().date()
    now_time = timezone.localtime().time()
    
    # Validate check-in time
    if not is_valid_check_in_time(now_time):
        return create_json_response(
            False, 
            'Check-in is only allowed between 08:00 - 09:15',
            'error'
        )
    
    # Get or create today's attendance record
    is_late = determine_late_status(now_time)
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={
            'check_in_time': now_time,
            'status': 'late' if is_late else 'present',
            'is_late': is_late
        }
    )
    
    if not created and attendance.check_in_time:
        return create_json_response(
            False, 
            'You have already checked in today',
            'warning'
        )
    
    # Update if not already checked in
    if not attendance.check_in_time:
        attendance.check_in_time = now_time
        attendance.status = 'late' if is_late else 'present'
        attendance.is_late = is_late
        attendance.save()
    
    # Return appropriate response based on late status
    if attendance.is_late:
        return create_json_response(
            True,
            f'🕘 Checked in LATE at {now_time.strftime("%H:%M")}. Please be on time tomorrow.',
            'warning',
            status='late'
        )
    else:
        return create_json_response(
            True,
            f'✅ Successfully checked in ON TIME at {now_time.strftime("%H:%M")}. Have a great day!',
            'success',
            status='on_time'
        )

@login_required
def check_out(request):
    """Handle check-out functionality"""
    if request.method != 'POST':
        return create_json_response(False, 'Invalid request method', 'error')
    
    employee = get_employee_or_none(request.user)
    if not employee:
        return create_json_response(False, 'Employee profile not found', 'error')
    
    today = timezone.localtime().date()
    now_time = timezone.localtime().time()
    
    # Validate check-out time
    if not is_valid_check_out_time(now_time):
        return create_json_response(
            False,
            'Check-out is only allowed after 17:00',
            'error'
        )
    
    # Get today's attendance record
    attendance = get_today_attendance(employee, today)
    if not attendance:
        return create_json_response(
            False,
            'No check-in record found for today',
            'error'
        )
    
    if not attendance.check_in_time:
        return create_json_response(
            False,
            'You must check in first before checking out',
            'warning'
        )
    
    if attendance.check_out_time:
        return create_json_response(
            False,
            'You have already checked out today',
            'warning'
        )
    
    # Calculate work duration
    work_duration = calculate_work_duration(attendance.check_in_time, now_time, today)
    
    # Check minimum work hours (8 hours)
    if work_duration < 8.0:
        return create_json_response(
            False,
            f'Minimum work time is 8 hours. You have worked {work_duration:.1f} hours. Please check out after 17:00 if you started at 09:00.',
            'warning'
        )
    
    # Update attendance record
    attendance.check_out_time = now_time
    attendance.save()
    
    return create_json_response(
        True,
        f'🏁 Successfully checked out at {now_time.strftime("%H:%M")}. You worked for {work_duration:.1f} hours today. Great job!',
        'success',
        work_duration=f'{work_duration:.1f} hours'
    )
