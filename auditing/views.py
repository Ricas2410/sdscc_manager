"""
Auditing Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal

from .models import AuditLog, FinancialAuditReport, AuditFlag
from core.models import Area, District, Branch, FiscalYear


@login_required
def audit_logs(request):
    """View audit logs."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    logs = AuditLog.objects.select_related('user', 'branch').order_by('-timestamp')
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    return render(request, 'auditing/audit_logs.html', {'logs': logs, 'actions': AuditLog.Action.choices})


@login_required
def audit_reports(request):
    """View audit reports."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    reports = FinancialAuditReport.objects.all().order_by('-period_end')
    return render(request, 'auditing/audit_reports.html', {'reports': reports})


@login_required
def audit_flags(request):
    """View audit flags."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    flags = AuditFlag.objects.select_related('branch').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        flags = flags.filter(status=status)
    
    return render(request, 'auditing/audit_flags.html', {'flags': flags})


@login_required
def auditor_contributions(request):
    """Auditor view for all contributions with hierarchical filtering."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from contributions.models import Contribution, ContributionType
    
    # Get filters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    contribution_type_id = request.GET.get('contribution_type')
    
    fiscal_year = FiscalYear.get_current()
    
    # Base queryset
    contributions = Contribution.objects.filter(
        fiscal_year=fiscal_year
    ).select_related('branch__district__area', 'contribution_type', 'member', 'created_by')
    
    # Apply hierarchical filters
    districts = District.objects.filter(is_active=True)
    branches = Branch.objects.filter(is_active=True)
    
    if area_id:
        contributions = contributions.filter(branch__district__area_id=area_id)
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    
    if district_id:
        contributions = contributions.filter(branch__district_id=district_id)
        branches = branches.filter(district_id=district_id)
    
    if branch_id:
        contributions = contributions.filter(branch_id=branch_id)
    
    if from_date:
        contributions = contributions.filter(date__gte=from_date)
    if to_date:
        contributions = contributions.filter(date__lte=to_date)
    
    if contribution_type_id:
        contributions = contributions.filter(contribution_type_id=contribution_type_id)
    
    # Calculate statistics
    total_amount = contributions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_count = contributions.count()
    
    # Order by date descending
    contributions = contributions.order_by('-date', '-created_at')
    
    # Paginate
    paginator = Paginator(contributions, 50)
    page = request.GET.get('page')
    contributions = paginator.get_page(page)
    
    context = {
        'contributions': contributions,
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'districts': districts.order_by('name'),
        'branches': branches.order_by('name'),
        'contribution_types': ContributionType.objects.filter(is_active=True).order_by('name'),
        'total_amount': total_amount,
        'total_count': total_count,
        'fiscal_year': fiscal_year,
        'selected_area': area_id,
        'selected_district': district_id,
        'selected_branch': branch_id,
        'selected_type': contribution_type_id,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'auditing/contributions.html', context)


@login_required
def auditor_expenditures(request):
    """Auditor view for all expenditures with hierarchical filtering."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from expenditure.models import Expenditure, ExpenditureCategory
    
    # Get filters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category_id = request.GET.get('category')
    level = request.GET.get('level')
    
    fiscal_year = FiscalYear.get_current()
    
    # Base queryset
    expenditures = Expenditure.objects.filter(
        fiscal_year=fiscal_year
    ).select_related('branch__district__area', 'category', 'created_by', 'approved_by')
    
    # Apply hierarchical filters
    districts = District.objects.filter(is_active=True)
    branches = Branch.objects.filter(is_active=True)
    
    if area_id:
        expenditures = expenditures.filter(
            Q(branch__district__area_id=area_id) | Q(level='mission')
        )
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    
    if district_id:
        expenditures = expenditures.filter(
            Q(branch__district_id=district_id) | Q(level='mission')
        )
        branches = branches.filter(district_id=district_id)
    
    if branch_id:
        expenditures = expenditures.filter(branch_id=branch_id)
    
    if from_date:
        expenditures = expenditures.filter(date__gte=from_date)
    if to_date:
        expenditures = expenditures.filter(date__lte=to_date)
    
    if category_id:
        expenditures = expenditures.filter(category_id=category_id)
    
    if level:
        expenditures = expenditures.filter(level=level)
    
    # Calculate statistics
    total_amount = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_count = expenditures.count()
    approved_amount = expenditures.filter(
        Q(status='approved') | Q(status='paid')
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    pending_amount = expenditures.filter(status='pending').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Order by date descending
    expenditures = expenditures.order_by('-date', '-created_at')
    
    # Paginate
    paginator = Paginator(expenditures, 50)
    page = request.GET.get('page')
    expenditures = paginator.get_page(page)
    
    context = {
        'expenditures': expenditures,
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'districts': districts.order_by('name'),
        'branches': branches.order_by('name'),
        'categories': ExpenditureCategory.objects.filter(is_active=True).order_by('name'),
        'total_amount': total_amount,
        'total_count': total_count,
        'approved_amount': approved_amount,
        'pending_amount': pending_amount,
        'fiscal_year': fiscal_year,
        'selected_area': area_id,
        'selected_district': district_id,
        'selected_branch': branch_id,
        'selected_category': category_id,
        'selected_level': level,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'auditing/expenditures.html', context)


@login_required
def auditor_financial_reports(request):
    """Generate financial reports for branches, districts, and areas with multiple time periods."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from contributions.models import Contribution
    from expenditure.models import Expenditure
    from reports.models import MonthlyReport
    from core.models import Area, District, Branch
    
    # Get filter parameters
    report_level = request.GET.get('level', 'branch')  # branch, district, area, individual
    entity_id = request.GET.get('entity_id')
    time_period = request.GET.get('period', 'monthly')  # monthly, quarterly, yearly
    year = request.GET.get('year')
    month = request.GET.get('month')
    quarter = request.GET.get('quarter')
    
    fiscal_year = FiscalYear.get_current()
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    if not year:
        year = current_year
    else:
        year = int(year)
    
    if not month:
        month = current_month
    else:
        month = int(month)
    
    reports_data = []
    period_label = ''
    
    # Generate reports based on level and time period
    if report_level == 'branch':
        # Generate branch-level financial reports
        branches = Branch.objects.filter(is_active=True)
        
        if time_period == 'monthly':
            if month and year:
                period_label = f"{['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month]} {year}"
                
                for branch in branches:
                    monthly_report = MonthlyReport.objects.filter(
                        branch=branch, year=year, month=month
                    ).first()
                    
                    if monthly_report:
                        reports_data.append({
                            'entity': branch,
                            'entity_name': branch.name,
                            'period': period_label,
                            'total_contributions': monthly_report.total_contributions,
                            'total_expenditure': monthly_report.total_expenditure,
                            'net_balance': monthly_report.total_contributions - monthly_report.total_expenditure,
                            'tithe_amount': monthly_report.tithe_amount,
                            'offering_amount': monthly_report.offering_amount,
                            'mission_remittance_due': monthly_report.mission_remittance_due,
                        })
        
        elif time_period == 'quarterly':
            if quarter and year:
                quarter = int(quarter)
                months_in_quarter = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)][quarter - 1]
                period_label = f"Q{quarter} {year}"
                
                for branch in branches:
                    total_contrib = Contribution.objects.filter(
                        branch=branch,
                        date__year=year,
                        date__month__in=months_in_quarter,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    total_expend = Expenditure.objects.filter(
                        branch=branch,
                        date__year=year,
                        date__month__in=months_in_quarter,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    if total_contrib > 0 or total_expend > 0:
                        reports_data.append({
                            'entity': branch,
                            'entity_name': branch.name,
                            'period': period_label,
                            'total_contributions': total_contrib,
                            'total_expenditure': total_expend,
                            'net_balance': total_contrib - total_expend,
                        })
        
        elif time_period == 'yearly':
            period_label = f"Year {year}"
            
            for branch in branches:
                total_contrib = Contribution.objects.filter(
                    branch=branch,
                    date__year=year,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                total_expend = Expenditure.objects.filter(
                    branch=branch,
                    date__year=year,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                if total_contrib > 0 or total_expend > 0:
                    reports_data.append({
                        'entity': branch,
                        'entity_name': branch.name,
                        'period': period_label,
                        'total_contributions': total_contrib,
                        'total_expenditure': total_expend,
                        'net_balance': total_contrib - total_expend,
                    })
    
    elif report_level == 'district':
        # Generate district-level financial reports
        districts = District.objects.filter(is_active=True)
        
        if time_period == 'monthly':
            if month and year:
                period_label = f"{['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month]} {year}"
                
                for district in districts:
                    total_contrib = Contribution.objects.filter(
                        branch__district=district,
                        date__year=year,
                        date__month=month,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    total_expend = Expenditure.objects.filter(
                        branch__district=district,
                        date__year=year,
                        date__month=month,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    if total_contrib > 0 or total_expend > 0:
                        reports_data.append({
                            'entity': district,
                            'entity_name': f"{district.name} ({district.area.name})",
                            'period': period_label,
                            'total_contributions': total_contrib,
                            'total_expenditure': total_expend,
                            'net_balance': total_contrib - total_expend,
                        })
        
        elif time_period == 'quarterly':
            if quarter and year:
                quarter = int(quarter)
                months_in_quarter = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)][quarter - 1]
                period_label = f"Q{quarter} {year}"
                
                for district in districts:
                    total_contrib = Contribution.objects.filter(
                        branch__district=district,
                        date__year=year,
                        date__month__in=months_in_quarter,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    total_expend = Expenditure.objects.filter(
                        branch__district=district,
                        date__year=year,
                        date__month__in=months_in_quarter,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    if total_contrib > 0 or total_expend > 0:
                        reports_data.append({
                            'entity': district,
                            'entity_name': f"{district.name} ({district.area.name})",
                            'period': period_label,
                            'total_contributions': total_contrib,
                            'total_expenditure': total_expend,
                            'net_balance': total_contrib - total_expend,
                        })
        
        elif time_period == 'yearly':
            period_label = f"Year {year}"
            
            for district in districts:
                total_contrib = Contribution.objects.filter(
                    branch__district=district,
                    date__year=year,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                total_expend = Expenditure.objects.filter(
                    branch__district=district,
                    date__year=year,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                if total_contrib > 0 or total_expend > 0:
                    reports_data.append({
                        'entity': district,
                        'entity_name': f"{district.name} ({district.area.name})",
                        'period': period_label,
                        'total_contributions': total_contrib,
                        'total_expenditure': total_expend,
                        'net_balance': total_contrib - total_expend,
                    })
    
    elif report_level == 'area':
        # Generate area-level financial reports
        areas = Area.objects.filter(is_active=True)
        
        if time_period == 'monthly':
            if month and year:
                period_label = f"{['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month]} {year}"
                
                for area in areas:
                    total_contrib = Contribution.objects.filter(
                        branch__district__area=area,
                        date__year=year,
                        date__month=month,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    total_expend = Expenditure.objects.filter(
                        branch__district__area=area,
                        date__year=year,
                        date__month=month,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    if total_contrib > 0 or total_expend > 0:
                        reports_data.append({
                            'entity': area,
                            'entity_name': area.name,
                            'period': period_label,
                            'total_contributions': total_contrib,
                            'total_expenditure': total_expend,
                            'net_balance': total_contrib - total_expend,
                        })
        
        elif time_period == 'quarterly':
            if quarter and year:
                quarter = int(quarter)
                months_in_quarter = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)][quarter - 1]
                period_label = f"Q{quarter} {year}"
                
                for area in areas:
                    total_contrib = Contribution.objects.filter(
                        branch__district__area=area,
                        date__year=year,
                        date__month__in=months_in_quarter,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    total_expend = Expenditure.objects.filter(
                        branch__district__area=area,
                        date__year=year,
                        date__month__in=months_in_quarter,
                        fiscal_year=fiscal_year
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    if total_contrib > 0 or total_expend > 0:
                        reports_data.append({
                            'entity': area,
                            'entity_name': area.name,
                            'period': period_label,
                            'total_contributions': total_contrib,
                            'total_expenditure': total_expend,
                            'net_balance': total_contrib - total_expend,
                        })
        
        elif time_period == 'yearly':
            period_label = f"Year {year}"
            
            for area in areas:
                total_contrib = Contribution.objects.filter(
                    branch__district__area=area,
                    date__year=year,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                total_expend = Expenditure.objects.filter(
                    branch__district__area=area,
                    date__year=year,
                    fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                if total_contrib > 0 or total_expend > 0:
                    reports_data.append({
                        'entity': area,
                        'entity_name': area.name,
                        'period': period_label,
                        'total_contributions': total_contrib,
                        'total_expenditure': total_expend,
                        'net_balance': total_contrib - total_expend,
                    })
    
    elif report_level == 'individual':
        # Generate individual member reports
        from accounts.models import User

        # Support lookup by member_id (e.g., "AN001") or UUID
        member_id_input = request.GET.get('member_id', '').strip()

        if member_id_input:
            # Try to find by member_id first (e.g., "AN001")
            member = User.objects.filter(member_id__iexact=member_id_input).first()
            if not member:
                # Try UUID lookup
                try:
                    member = User.objects.filter(pk=member_id_input).first()
                except Exception:
                    member = None
        elif entity_id:
            member = User.objects.filter(pk=entity_id).first()
        else:
            member = None
        
        if member:
            if time_period == 'monthly':
                if month and year:
                    period_label = f"{['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month]} {year}"
                    
                    total_contrib = Contribution.objects.filter(
                        member=member,
                        date__year=year,
                        date__month=month
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    reports_data.append({
                        'entity': member,
                        'entity_name': member.get_full_name(),
                        'period': period_label,
                        'total_contributions': total_contrib,
                        'total_expenditure': Decimal('0.00'),
                        'net_balance': total_contrib,
                    })
            
            elif time_period == 'quarterly':
                if quarter and year:
                    quarter = int(quarter)
                    months_in_quarter = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)][quarter - 1]
                    period_label = f"Q{quarter} {year}"
                    
                    total_contrib = Contribution.objects.filter(
                        member=member,
                        date__year=year,
                        date__month__in=months_in_quarter
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    reports_data.append({
                        'entity': member,
                        'entity_name': member.get_full_name(),
                        'period': period_label,
                        'total_contributions': total_contrib,
                        'total_expenditure': Decimal('0.00'),
                        'net_balance': total_contrib,
                    })
            
            elif time_period == 'yearly':
                period_label = f"Year {year}"
                
                total_contrib = Contribution.objects.filter(
                    member=member,
                    date__year=year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                reports_data.append({
                    'entity': member,
                    'entity_name': member.get_full_name(),
                    'period': period_label,
                    'total_contributions': total_contrib,
                    'total_expenditure': Decimal('0.00'),
                    'net_balance': total_contrib,
                })
    
    # Sort reports by entity name
    reports_data.sort(key=lambda x: x['entity_name'])
    
    # Calculate totals
    total_all_contributions = sum(r['total_contributions'] for r in reports_data)
    total_all_expenditure = sum(r['total_expenditure'] for r in reports_data)
    total_all_balance = sum(r['net_balance'] for r in reports_data)
    
    context = {
        'reports': reports_data,
        'report_level': report_level,
        'time_period': time_period,
        'year': year,
        'month': month,
        'quarter': quarter,
        'period_label': period_label,
        'total_contributions': total_all_contributions,
        'total_expenditure': total_all_expenditure,
        'total_balance': total_all_balance,
        'fiscal_year': fiscal_year,
        'current_year': current_year,
        'current_month': current_month,
    }
    
    return render(request, 'auditing/financial_reports.html', context)


@login_required
def member_lookup_report(request):
    """Look up a member by ID and generate their contribution and attendance reports."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    from accounts.models import User
    from contributions.models import Contribution
    from attendance.models import AttendanceRecord
    from django.utils import timezone

    member = None
    contributions = []
    attendance_records = []
    contribution_summary = {}
    attendance_summary = {}

    member_id_input = request.GET.get('member_id', '').strip()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if member_id_input:
        # Try to find by member_id first (e.g., "AN001")
        member = User.objects.filter(member_id__iexact=member_id_input).first()
        if not member:
            # Try phone number lookup
            member = User.objects.filter(phone__icontains=member_id_input).first()

        if member:
            # Get contributions
            contrib_query = Contribution.objects.filter(member=member).select_related('contribution_type', 'branch')
            if from_date:
                contrib_query = contrib_query.filter(date__gte=from_date)
            if to_date:
                contrib_query = contrib_query.filter(date__lte=to_date)
            contributions = contrib_query.order_by('-date')[:100]

            # Contribution summary
            contribution_summary = {
                'total_amount': contrib_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
                'count': contrib_query.count(),
                'by_type': list(contrib_query.values('contribution_type__name').annotate(
                    total=Sum('amount'),
                    count=Count('id')
                ).order_by('-total'))
            }

            # Get attendance
            attend_query = AttendanceRecord.objects.filter(member=member).select_related('session', 'session__service_type')
            if from_date:
                attend_query = attend_query.filter(session__date__gte=from_date)
            if to_date:
                attend_query = attend_query.filter(session__date__lte=to_date)
            attendance_records = attend_query.order_by('-session__date')[:100]

            # Attendance summary
            total_sessions = attend_query.count()
            present_count = attend_query.filter(status='present').count()
            attendance_summary = {
                'total_sessions': total_sessions,
                'present_count': present_count,
                'absent_count': attend_query.filter(status='absent').count(),
                'attendance_rate': (present_count / total_sessions * 100) if total_sessions > 0 else 0
            }
        else:
            messages.warning(request, f'No member found with ID "{member_id_input}"')

    context = {
        'member': member,
        'member_id_input': member_id_input,
        'contributions': contributions,
        'contribution_summary': contribution_summary,
        'attendance_records': attendance_records,
        'attendance_summary': attendance_summary,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'auditing/member_lookup_report.html', context)


@login_required
def export_financial_report_pdf(request):
    """Export financial reports as PDF."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from contributions.models import Contribution
    from expenditure.models import Expenditure
    from core.models import Area, District, Branch, FiscalYear, SiteSettings

    try:
        import weasyprint
    except ImportError:
        messages.error(request, 'PDF export not available. WeasyPrint not installed.')
        return redirect('auditing:financial_reports')

    # Get parameters from request
    report_level = request.GET.get('level', 'branch')
    time_period = request.GET.get('period', 'monthly')
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    quarter = request.GET.get('quarter')

    fiscal_year = FiscalYear.get_current()
    reports_data = []
    period_label = ''

    # Generate period label
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    if time_period == 'monthly':
        period_label = f"{month_names[month]} {year}"
    elif time_period == 'quarterly' and quarter:
        period_label = f"Q{quarter} {year}"
    else:
        period_label = f"Year {year}"

    # Generate reports based on level
    if report_level == 'branch':
        branches = Branch.objects.filter(is_active=True)
        for branch in branches:
            if time_period == 'monthly':
                total_contrib = Contribution.objects.filter(
                    branch=branch, date__year=year, date__month=month, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch=branch, date__year=year, date__month=month, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            elif time_period == 'quarterly' and quarter:
                months_in_quarter = [(1,2,3), (4,5,6), (7,8,9), (10,11,12)][int(quarter)-1]
                total_contrib = Contribution.objects.filter(
                    branch=branch, date__year=year, date__month__in=months_in_quarter, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch=branch, date__year=year, date__month__in=months_in_quarter, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            else:
                total_contrib = Contribution.objects.filter(
                    branch=branch, date__year=year, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch=branch, date__year=year, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            if total_contrib > 0 or total_expend > 0:
                reports_data.append({
                    'entity_name': branch.name,
                    'total_contributions': total_contrib,
                    'total_expenditure': total_expend,
                    'net_balance': total_contrib - total_expend,
                })

    elif report_level == 'district':
        districts = District.objects.filter(is_active=True)
        for district in districts:
            if time_period == 'monthly':
                total_contrib = Contribution.objects.filter(
                    branch__district=district, date__year=year, date__month=month, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch__district=district, date__year=year, date__month=month, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            else:
                total_contrib = Contribution.objects.filter(
                    branch__district=district, date__year=year, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch__district=district, date__year=year, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            if total_contrib > 0 or total_expend > 0:
                reports_data.append({
                    'entity_name': f"{district.name} ({district.area.name})",
                    'total_contributions': total_contrib,
                    'total_expenditure': total_expend,
                    'net_balance': total_contrib - total_expend,
                })

    elif report_level == 'area':
        areas = Area.objects.filter(is_active=True)
        for area in areas:
            if time_period == 'monthly':
                total_contrib = Contribution.objects.filter(
                    branch__district__area=area, date__year=year, date__month=month, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch__district__area=area, date__year=year, date__month=month, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            else:
                total_contrib = Contribution.objects.filter(
                    branch__district__area=area, date__year=year, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_expend = Expenditure.objects.filter(
                    branch__district__area=area, date__year=year, fiscal_year=fiscal_year
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            if total_contrib > 0 or total_expend > 0:
                reports_data.append({
                    'entity_name': area.name,
                    'total_contributions': total_contrib,
                    'total_expenditure': total_expend,
                    'net_balance': total_contrib - total_expend,
                })

    # Calculate totals
    total_contributions = sum(r['total_contributions'] for r in reports_data)
    total_expenditure = sum(r['total_expenditure'] for r in reports_data)
    total_balance = sum(r['net_balance'] for r in reports_data)

    site_settings = SiteSettings.get_settings()

    # Render PDF
    html_string = render_to_string('auditing/financial_report_pdf.html', {
        'reports': reports_data,
        'report_level': report_level,
        'period_label': period_label,
        'total_contributions': total_contributions,
        'total_expenditure': total_expenditure,
        'total_balance': total_balance,
        'site_settings': site_settings,
        'generated_date': timezone.now(),
        'generated_by': request.user.get_full_name(),
    })

    html = weasyprint.HTML(string=html_string)
    pdf = html.write_pdf()

    filename = f"financial_report_{report_level}_{period_label.replace(' ', '_')}.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_member_report_pdf(request):
    """Export member contribution and attendance report as PDF."""
    if not (request.user.is_mission_admin or request.user.is_auditor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from accounts.models import User
    from contributions.models import Contribution
    from attendance.models import AttendanceRecord
    from core.models import SiteSettings

    try:
        import weasyprint
    except ImportError:
        messages.error(request, 'PDF export not available.')
        return redirect('auditing:member_lookup')

    member_id_input = request.GET.get('member_id', '').strip()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    member = User.objects.filter(member_id__iexact=member_id_input).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('auditing:member_lookup')

    # Get contributions
    contrib_query = Contribution.objects.filter(member=member).select_related('contribution_type')
    if from_date:
        contrib_query = contrib_query.filter(date__gte=from_date)
    if to_date:
        contrib_query = contrib_query.filter(date__lte=to_date)
    contributions = contrib_query.order_by('-date')

    contribution_summary = {
        'total_amount': contrib_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'count': contrib_query.count(),
    }

    # Get attendance
    attend_query = AttendanceRecord.objects.filter(member=member).select_related('session', 'session__service_type')
    if from_date:
        attend_query = attend_query.filter(session__date__gte=from_date)
    if to_date:
        attend_query = attend_query.filter(session__date__lte=to_date)
    attendance_records = attend_query.order_by('-session__date')

    total_sessions = attend_query.count()
    present_count = attend_query.filter(status='present').count()
    attendance_summary = {
        'total_sessions': total_sessions,
        'present_count': present_count,
        'attendance_rate': (present_count / total_sessions * 100) if total_sessions > 0 else 0
    }

    site_settings = SiteSettings.get_settings()

    html_string = render_to_string('auditing/member_report_pdf.html', {
        'member': member,
        'contributions': contributions,
        'contribution_summary': contribution_summary,
        'attendance_records': attendance_records,
        'attendance_summary': attendance_summary,
        'from_date': from_date,
        'to_date': to_date,
        'site_settings': site_settings,
        'generated_date': timezone.now(),
        'generated_by': request.user.get_full_name(),
    })

    html = weasyprint.HTML(string=html_string)
    pdf = html.write_pdf()

    filename = f"member_report_{member.member_id}_{timezone.now().strftime('%Y%m%d')}.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
