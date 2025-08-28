from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('profile/', views.employee_profile_view, name='employee_profile_view'),
    path('profile/edit/', views.employee_profile_edit, name='employee_profile_edit'),
    path('<str:employee_id>/', views.employee_detail, name='employee_detail'),
    path('<str:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('<str:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    path('<str:employee_id>/activate/', views.employee_activate, name='employee_activate'),
    path('bulk/actions/', views.employee_bulk_actions, name='employee_bulk_actions'),
]
