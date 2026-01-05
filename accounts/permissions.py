"""
Role-based permissions for SDSCC
"""

from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def mission_admin_required(function):
    """Decorator for views that require mission admin access."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_mission_admin:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Mission Admin privileges required.')
        return redirect('core:dashboard')
    return wrap


def branch_admin_required(function):
    """Decorator for views that require branch admin access."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_mission_admin or request.user.is_branch_executive:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Branch Admin privileges required.')
        return redirect('core:dashboard')
    return wrap


def finance_management_required(function):
    """Decorator for views that require finance management permissions."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.can_manage_finances:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Finance management privileges required.')
        return redirect('core:dashboard')
    return wrap


def finance_view_required(function):
    """Decorator for views that require finance viewing permissions."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.can_view_finances:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Finance viewing privileges required.')
        return redirect('core:dashboard')
    return wrap


def area_executive_required(function):
    """Decorator for views that require area executive access."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_mission_admin or request.user.is_area_executive:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Area Executive privileges required.')
        return redirect('core:dashboard')
    return wrap


def district_executive_required(function):
    """Decorator for views that require district executive access."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_mission_admin or request.user.is_district_executive:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. District Executive privileges required.')
        return redirect('core:dashboard')
    return wrap


def auditor_required(function):
    """Decorator for views that require auditor access."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_mission_admin or request.user.is_auditor:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Auditor privileges required.')
        return redirect('core:dashboard')
    return wrap


def pastor_required(function):
    """Decorator for views that require pastor access."""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_mission_admin or request.user.is_pastor:
            return function(request, *args, **kwargs)
        messages.error(request, 'Access denied. Pastor privileges required.')
        return redirect('core:dashboard')
    return wrap


def can_view_area_finances(user, area_id):
    """Check if user can view area finances."""
    if user.is_mission_admin or user.is_auditor:
        return True
    if user.is_area_executive and user.managed_area and str(user.managed_area.id) == area_id:
        return True
    return False


def can_view_district_finances(user, district_id):
    """Check if user can view district finances."""
    if user.is_mission_admin or user.is_auditor:
        return True
    if user.is_area_executive and user.managed_area:
        from core.models import District
        try:
            district = District.objects.get(pk=district_id)
            if district.area == user.managed_area:
                return True
        except District.DoesNotExist:
            pass
    if user.is_district_executive and user.managed_district and str(user.managed_district.id) == district_id:
        return True
    return False


def can_view_branch_finances(user, branch_id):
    """Check if user can view branch finances."""
    if user.is_mission_admin or user.is_auditor:
        return True
    if user.is_area_executive and user.managed_area:
        from core.models import Branch
        try:
            branch = Branch.objects.get(pk=branch_id)
            if branch.district.area == user.managed_area:
                return True
        except Branch.DoesNotExist:
            pass
    if user.is_district_executive and user.managed_district:
        from core.models import Branch
        try:
            branch = Branch.objects.get(pk=branch_id)
            if branch.district == user.managed_district:
                return True
        except Branch.DoesNotExist:
            pass
    if user.is_branch_executive and user.branch and str(user.branch.id) == branch_id:
        return True
    if user.is_pastor and user.branch and str(user.branch.id) == branch_id:
        return True
    return False
