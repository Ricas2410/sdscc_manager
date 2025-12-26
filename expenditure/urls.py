"""
Expenditure URL Configuration
"""

from django.urls import path
from . import views

app_name = 'expenditure'

urlpatterns = [
    path('', views.expenditure_list, name='list'),
    path('add/', views.expenditure_add, name='add'),
    path('categories/', views.expenditure_categories, name='categories'),
    path('utilities/', views.utility_bills, name='utilities'),
    path('welfare/', views.welfare_payments, name='welfare'),
    path('assets/', views.assets_list, name='assets'),
    path('<uuid:expenditure_id>/', views.expenditure_detail, name='detail'),
]
