"""
Monthly Closing Views - UI for month-end operations
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from datetime import date, datetime
import calendar

from core.models import Branch, MonthlyClose
from core.monthly_closing import MonthlyClosingService
from contributions.models import Contribution, ContributionType
from expenditure.models import Expenditure


@login_required
def check_monthly_closing_status(request):
    """API endpoint to check if a month is closed."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    month = request.GET.get('month')
    year = request.GET.get('year')

    if not month or not year:
        return JsonResponse({'error': 'Month and year required'}, status=400)

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid month or year'}, status=400)

    # Get user's branch
    branch = request.user.branch
    if not branch:
        return JsonResponse({'is_closed': False})

    # Check if month is closed
    monthly_close = MonthlyClose.objects.filter(
        branch=branch,
        month=month,
        year=year,
        is_closed=True
    ).first()

    return JsonResponse({
        'is_closed': monthly_close is not None,
        'month': month,
        'year': year
    })


@login_required
def monthly_closing_dashboard(request):
    """Dashboard for monthly closing operations."""
    if not (request.user.is_mission_admin or request.user.is_any_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Initialize hierarchy-based filtering
    user_scope = 'mission'  # Default for mission admin
    if request.user.is_branch_executive and request.user.branch:
        user_scope = 'branch'
    elif request.user.is_district_executive and request.user.managed_district:
        user_scope = 'district'
    elif request.user.is_area_executive and request.user.managed_area:
        user_scope = 'area'
    
    # Get branches based on user hierarchy
    if user_scope == 'area':
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True)
        selected_branch_id = request.GET.get('branch')
        if selected_branch_id:
            branch = get_object_or_404(Branch, pk=selected_branch_id, district__area=request.user.managed_area)
        else:
            branch = branches.first()
    elif user_scope == 'district':
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
        selected_branch_id = request.GET.get('branch')
        if selected_branch_id:
            branch = get_object_or_404(Branch, pk=selected_branch_id, district=request.user.managed_district)
        else:
            branch = branches.first()
    elif user_scope == 'branch':
        branch = request.user.branch
        branches = Branch.objects.filter(id=branch.id) if branch else Branch.objects.none()
    else:
        branches = Branch.objects.filter(is_active=True)
        selected_branch_id = request.GET.get('branch')
        if selected_branch_id:
            branch = get_object_or_404(Branch, pk=selected_branch_id)
        else:
            branch = branches.first()
    
    if not branch:
        messages.error(request, 'No branch available.')
        return redirect('core:dashboard')
    
    # Get current month and year
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    # Get monthly close record
    monthly_close = MonthlyClose.objects.filter(
        branch=branch,
        month=selected_month,
        year=selected_year
    ).first()
    
    # Get monthly summary
    service = MonthlyClosingService(branch, selected_month, selected_year)
    summary = service.get_monthly_summary()
    
    # Check if can close
    can_close, close_message = service.can_close_month()
    
    # Get list of closed months for this branch
    closed_months = MonthlyClose.objects.filter(
        branch=branch,
        is_closed=True
    ).order_by('-year', '-month')[:12]
    
    context = {
        'branch': branch,
        'branches': branches,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': calendar.month_name[selected_month],
        'monthly_close': monthly_close,
        'summary': summary,
        'can_close': can_close,
        'close_message': close_message,
        'closed_months': closed_months,
        'is_closed': summary['is_closed'],
        'available_years': list(range(today.year - 3, today.year + 1)),
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
    }
    
    return render(request, 'core/monthly_closing_dashboard.html', context)


@login_required
def close_month(request):
    """Close a month."""
    if not (request.user.is_mission_admin or request.user.is_branch_executive):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    branch_id = request.POST.get('branch_id')
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    
    branch = get_object_or_404(Branch, pk=branch_id)
    
    # Check permissions
    if not request.user.is_mission_admin and branch != request.user.branch:
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        service = MonthlyClosingService(branch, month, year)
        monthly_close = service.close_month(request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Month {calendar.month_name[month]} {year} closed successfully',
            'monthly_close_id': str(monthly_close.id)
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


@login_required
def reopen_month(request):
    """Reopen a closed month (Mission Admin only)."""
    if not request.user.is_mission_admin:
        return JsonResponse({'success': False, 'message': 'Only Mission Admin can reopen months'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    branch_id = request.POST.get('branch_id')
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    
    branch = get_object_or_404(Branch, pk=branch_id)
    
    try:
        service = MonthlyClosingService(branch, month, year)
        monthly_close = service.reopen_month(request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Month {calendar.month_name[month]} {year} reopened successfully'
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


@login_required
def monthly_report_view(request):
    """View monthly report for a closed month."""
    if not (request.user.can_view_all_finances or request.user.can_manage_finances):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get parameters
    branch_id = request.GET.get('branch')
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    
    if request.user.is_mission_admin:
        branches = Branch.objects.filter(is_active=True)
        if branch_id:
            branch = get_object_or_404(Branch, pk=branch_id)
        else:
            branch = branches.first()
    else:
        branch = request.user.branch
        branches = Branch.objects.filter(id=branch.id) if branch else Branch.objects.none()
    
    if not branch:
        messages.error(request, 'No branch selected.')
        return redirect('core:dashboard')
    
    # Get monthly summary
    service = MonthlyClosingService(branch, month, year)
    summary = service.get_monthly_summary()
    
    # Get monthly close record
    monthly_close = MonthlyClose.objects.filter(
        branch=branch,
        month=month,
        year=year
    ).first()
    
    context = {
        'branch': branch,
        'branches': branches,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'summary': summary,
        'monthly_close': monthly_close,
        'is_closed': summary['is_closed'],
        'available_years': list(range(year - 3, year + 2)),
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
    }
    
    return render(request, 'core/monthly_report.html', context)


@login_required
def monthly_report_pdf(request):
    """Generate PDF of monthly report."""
    from django.template.loader import render_to_string
    import tempfile
    
    try:
        from weasyprint import HTML
        WEASYPRINT_AVAILABLE = True
    except ImportError:
        WEASYPRINT_AVAILABLE = False
    
    if not request.user.can_view_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get parameters
    branch_id = request.GET.get('branch')
    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    
    if request.user.is_mission_admin:
        if branch_id:
            branch = get_object_or_404(Branch, pk=branch_id)
        else:
            branch = Branch.objects.filter(is_active=True).first()
    else:
        branch = request.user.branch
    
    if not branch:
        messages.error(request, 'No branch selected.')
        return redirect('core:dashboard')
    
    # Get monthly summary
    service = MonthlyClosingService(branch, month, year)
    summary = service.get_monthly_summary()
    
    # Get monthly close record
    monthly_close = MonthlyClose.objects.filter(
        branch=branch,
        month=month,
        year=year
    ).first()
    
    # Get site settings for letterhead
    from core.models import SiteSettings
    site_settings = SiteSettings.get_settings()

    # Render HTML template
    html_string = render_to_string('core/monthly_report_pdf.html', {
        'branch': branch,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'summary': summary,
        'monthly_close': monthly_close,
        'generated_date': date.today(),
        'generated_by': request.user,
        'site_settings': site_settings,
    })
    
    # Generate PDF
    if not WEASYPRINT_AVAILABLE:
        messages.error(request, 'PDF generation is not available. Please install weasyprint or use the Excel export instead.')
        return redirect('core:monthly_report')
    
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    # Return PDF response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly_report_{branch.code}_{month}_{year}.pdf"'
    
    return response


@login_required
def check_edit_permission(request):
    """Check if a contribution/expenditure can be edited."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    item_type = request.POST.get('type')  # 'contribution' or 'expenditure'
    item_id = request.POST.get('id')
    
    try:
        if item_type == 'contribution':
            item = get_object_or_404(Contribution, pk=item_id)
            can_edit, message = MonthlyClosingService.can_edit_contribution(item, request.user)
        elif item_type == 'expenditure':
            item = get_object_or_404(Expenditure, pk=item_id)
            can_edit, message = MonthlyClosingService.can_edit_expenditure(item, request.user)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid type'}, status=400)
        
        return JsonResponse({
            'success': True,
            'can_edit': can_edit,
            'message': message
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
