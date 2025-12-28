"""
Attendance URL Configuration
"""

from django.urls import path
from . import views

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
    
    # Visitor tracking
    path('visitors/', views.visitor_list, name='visitors'),
    path('visitor/add/<uuid:session_id>/', views.add_visitor, name='add_visitor'),
    path('visitor/<uuid:visitor_id>/', views.visitor_detail, name='visitor_detail'),
]
