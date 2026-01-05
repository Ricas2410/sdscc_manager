"""
Attendance URL Configuration
"""

from django.urls import path
from . import views
from . import mission_staff_views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('add/', views.take_attendance, name='add'),  # Alias for take
    path('take/', views.take_attendance, name='take'),
    path('tracking/', views.attendance_tracking, name='tracking'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('session/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('member/<uuid:user_id>/', views.member_attendance, name='member_attendance'),
    
    # Weekly attendance reports
    path('weekly/', views.weekly_report, name='weekly_report'),
    path('weekly/branch/<uuid:branch_id>/<str:week_start>/', views.branch_weekly_detail, name='branch_weekly_detail'),
    
    # Visitor tracking
    path('visitors/', views.visitor_list, name='visitors'),
    path('visitor/add/<uuid:session_id>/', views.add_visitor, name='add_visitor'),
    path('visitor/<uuid:visitor_id>/', views.visitor_detail, name='visitor_detail'),
    
    # Mission Staff Attendance
    path('mission-staff/register/', mission_staff_views.mission_staff_attendance_register, name='mission_staff_register'),
    path('mission-staff/save/', mission_staff_views.save_mission_staff_attendance, name='mission_staff_save'),
    path('mission-staff/history/', mission_staff_views.mission_staff_attendance_history, name='mission_staff_history'),
    path('mission-staff/detail/<uuid:attendance_id>/', mission_staff_views.mission_staff_attendance_detail, name='mission_staff_detail'),
    path('mission-staff/override-lock/<uuid:attendance_id>/', mission_staff_views.override_attendance_lock, name='mission_staff_override_lock'),
    path('mission-staff/summary/', mission_staff_views.mission_staff_attendance_summary, name='mission_staff_summary'),
    
    # My Meetings - Staff view
    path('my-meetings/', mission_staff_views.my_meetings, name='my_meetings'),
]
