from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import Employee
from .forms import EmployeeForm, EmployeeSearchForm, EmployeeProfileForm
from .decorators import hr_admin_required

@login_required
@hr_admin_required
def employee_list(request):
    """List all employees with search and filter functionality"""
    form = EmployeeSearchForm(request.GET)
    employees = Employee.objects.select_related('user').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        department = form.cleaned_data.get('department')
        role = form.cleaned_data.get('role')
        is_active = form.cleaned_data.get('is_active')
        
        if search:
            employees = employees.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        if department:
            employees = employees.filter(department=department)
        
        if role:
            employees = employees.filter(role=role)
        
        if is_active:
            employees = employees.filter(is_active=is_active.lower() == 'true')
    
    # Pagination
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'employees': page_obj,
    }
    return render(request, 'employee/employee_list.html', context)

@login_required
@hr_admin_required
def employee_detail(request, employee_id):
    """View employee details"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    context = {
        'employee': employee,
    }
    return render(request, 'employee/employee_detail.html', context)

@login_required
@hr_admin_required
def employee_create(request):
    """Create new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                employee = form.save()
                success_msg = f'✅ Employee {employee.get_full_name()} (ID: {employee.employee_id}) has been created successfully! '
                success_msg += f'They have been assigned to {employee.get_department_display()} as {employee.get_role_display()}.'
                messages.success(request, success_msg)
                return redirect('employee_detail', employee_id=employee.employee_id)
            except Exception as e:
                messages.error(request, f'❌ Error creating employee: {str(e)}. Please check the form and try again.')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'employee/employee_form.html', context)

@login_required
@hr_admin_required
def employee_edit(request, employee_id):
    """Edit existing employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            try:
                employee = form.save()
                success_msg = f'✅ Employee {employee.get_full_name()} (ID: {employee.employee_id}) has been updated successfully! '
                success_msg += f'Current role: {employee.get_role_display()} in {employee.get_department_display()}.'
                messages.success(request, success_msg)
                return redirect('employee_detail', employee_id=employee.employee_id)
            except Exception as e:
                messages.error(request, f'❌ Error updating employee: {str(e)}. Please check the form and try again.')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
        'action': 'Edit',
    }
    return render(request, 'employee/employee_form.html', context)

@login_required
@hr_admin_required
@require_http_methods(["POST"])
def employee_delete(request, employee_id):
    """Delete employee (soft delete by setting is_active to False)"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    try:
        # Soft delete - set is_active to False
        employee.is_active = False
        employee.save()
        
        # Also deactivate the user account
        employee.user.is_active = False
        employee.user.save()
        
        success_msg = f'🚫 Employee {employee.get_full_name()} (ID: {employee.employee_id}) has been deactivated successfully. '
        success_msg += f'They will no longer be able to access the system until reactivated.'
        messages.success(request, success_msg)
    except Exception as e:
        messages.error(request, f'❌ Error deactivating employee: {str(e)}. Please try again or contact support.')
    
    return redirect('employee_list')

@login_required
@hr_admin_required
@require_http_methods(["POST"])
def employee_activate(request, employee_id):
    """Reactivate employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    try:
        employee.is_active = True
        employee.save()
        
        # Also reactivate the user account
        employee.user.is_active = True
        employee.user.save()
        
        success_msg = f'✅ Employee {employee.get_full_name()} (ID: {employee.employee_id}) has been reactivated successfully! '
        success_msg += f'They can now access the system again with their existing credentials.'
        messages.success(request, success_msg)
    except Exception as e:
        messages.error(request, f'❌ Error reactivating employee: {str(e)}. Please try again or contact support.')
    
    return redirect('employee_detail', employee_id=employee_id)

@login_required
@hr_admin_required
def employee_bulk_actions(request):
    """Handle bulk actions on employees"""
    if request.method == 'POST':
        action = request.POST.get('action')
        employee_ids = request.POST.getlist('employee_ids')
        
        if not employee_ids:
            messages.error(request, '⚠️ No employees selected. Please select at least one employee to perform bulk actions.')
            return redirect('employee_list')
        
        employees = Employee.objects.filter(employee_id__in=employee_ids)
        employee_count = len(employee_ids)
        
        if action == 'deactivate':
            employees.update(is_active=False)
            User.objects.filter(employee_profile__in=employees).update(is_active=False)
            success_msg = f'🚫 Successfully deactivated {employee_count} employee{"s" if employee_count > 1 else ""}. '
            success_msg += f'They will no longer be able to access the system until reactivated.'
            messages.success(request, success_msg)
        
        elif action == 'activate':
            employees.update(is_active=True)
            User.objects.filter(employee_profile__in=employees).update(is_active=True)
            success_msg = f'✅ Successfully activated {employee_count} employee{"s" if employee_count > 1 else ""}. '
            success_msg += f'They can now access the system with their existing credentials.'
            messages.success(request, success_msg)
        
        else:
            messages.error(request, '❌ Invalid action selected. Please choose a valid bulk action.')
    
    return redirect('employee_list')


@login_required
def employee_profile_view(request):
    """View employee's own profile"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, '❌ Employee profile not found. Please contact administrator.')
        return redirect('dashboard')
    
    context = {
        'employee': employee,
    }
    return render(request, 'employee/profile_view.html', context)


@login_required
def employee_profile_edit(request):
    """Edit employee's own profile"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, '❌ Employee profile not found. Please contact administrator.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            try:
                employee = form.save()
                messages.success(request, f'✅ Your profile has been updated successfully!')
                return redirect('employee_profile_view')
            except Exception as e:
                messages.error(request, f'❌ Error updating profile: {str(e)}. Please try again.')
    else:
        form = EmployeeProfileForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
    }
    return render(request, 'employee/profile_edit.html', context)
