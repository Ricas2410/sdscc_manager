"""
Core Views - Dashboard and administration views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta

from .models import Area, District, Branch, SiteSettings, FiscalYear


def get_pin_change_context(request):
    """Get PIN change context for dashboard views."""
    show_modal = request.session.get('show_pin_change_modal', False)
    return {
        'show_pin_change_modal': show_modal,
        'pin_change_required': request.session.get('pin_change_required', False),
    }


@login_required
def dashboard(request):
    """Main dashboard - redirects to role-specific dashboard."""
    user = request.user
    
    if user.is_mission_admin:
        return mission_dashboard(request)
    elif user.is_area_executive:
        return area_dashboard(request)
    elif user.is_district_executive:
        return district_dashboard(request)
    elif user.is_branch_executive:
        return branch_dashboard(request)
    elif user.is_auditor:
        return auditor_dashboard(request)
    elif user.is_pastor:
        return pastor_dashboard(request)
    elif user.is_staff_member:
        return staff_dashboard(request)
    else:
        return member_dashboard(request)


@login_required
def mission_dashboard(request):
    """Dashboard for Mission Admin."""
    from contributions.models import Contribution, Remittance
    from expenditure.models import Expenditure
    from accounts.models import User
    from attendance.models import WeeklyAttendance
    
    # Get current fiscal year
    fiscal_year = FiscalYear.get_current()
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Get current week's attendance
    weekly_attendance = WeeklyAttendance.get_current_week()
    
    # Get pending remittances with branch info
    pending_remittances_list = Remittance.objects.filter(
        status__in=['pending', 'sent']
    ).select_related('branch')[:5]
    
    # Statistics
    context = {
        'total_branches': Branch.objects.filter(is_active=True).count(),
        'total_districts': District.objects.filter(is_active=True).count(),
        'total_areas': Area.objects.filter(is_active=True).count(),
        'total_members': User.objects.filter(is_active=True).count(),
        'total_pastors': User.objects.filter(role='pastor', is_active=True).count(),
        
        # Financial summaries
        'monthly_contributions': Contribution.objects.filter(
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'monthly_expenditure': Expenditure.objects.filter(
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'pending_remittances': Remittance.objects.filter(
            status__in=['pending', 'sent']
        ).count(),
        
        'pending_remittances_list': pending_remittances_list,
        
        # Recent activities
        'recent_contributions': Contribution.objects.select_related(
            'branch', 'contribution_type', 'member'
        ).order_by('-created_at')[:10],
        
        'recent_branches': Branch.objects.filter(is_active=True).select_related(
            'district__area', 'pastor'
        ).order_by('-created_at')[:5],
        
        'fiscal_year': fiscal_year,
        'weekly_attendance': weekly_attendance,
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/mission_dashboard.html', context)


@login_required
def area_dashboard(request):
    """Dashboard for Area Executive."""
    user = request.user
    area = user.managed_area
    
    if not area:
        messages.warning(request, 'No area assigned to your account.')
        return redirect('core:dashboard')
    
    context = {
        'area': area,
        'districts': District.objects.filter(area=area, is_active=True),
        'branches': Branch.objects.filter(district__area=area, is_active=True),
        'branch_count': Branch.objects.filter(district__area=area, is_active=True).count(),
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/area_dashboard.html', context)


@login_required
def district_dashboard(request):
    """Dashboard for District Executive."""
    user = request.user
    district = user.managed_district
    
    if not district:
        messages.warning(request, 'No district assigned to your account.')
        return redirect('core:dashboard')
    
    context = {
        'district': district,
        'branches': Branch.objects.filter(district=district, is_active=True),
        'branch_count': Branch.objects.filter(district=district, is_active=True).count(),
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/district_dashboard.html', context)


@login_required
def branch_dashboard(request):
    """Dashboard for Branch Executive."""
    from contributions.models import Contribution, Remittance
    from expenditure.models import Expenditure
    from attendance.models import AttendanceSession
    
    user = request.user
    branch = user.branch
    
    if not branch:
        messages.warning(request, 'No branch assigned to your account.')
        return redirect('core:dashboard')
    
    fiscal_year = FiscalYear.get_current()
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    context = {
        'branch': branch,
        'member_count': branch.member_count,
        
        # Financial
        'monthly_contributions': Contribution.objects.filter(
            branch=branch,
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'monthly_expenditure': Expenditure.objects.filter(
            branch=branch,
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'local_balance': branch.local_balance,
        'tithe_target': branch.monthly_tithe_target,
        
        # Recent attendance
        'recent_attendance': AttendanceSession.objects.filter(
            branch=branch
        ).order_by('-date')[:5],
        
        # Pending remittance
        'pending_remittance': Remittance.objects.filter(
            branch=branch,
            status='pending'
        ).first(),
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/branch_dashboard.html', context)


@login_required
def auditor_dashboard(request):
    """Dashboard for Auditor / Board of Trustees."""
    from contributions.models import Contribution, Remittance
    from expenditure.models import Expenditure
    from auditing.models import AuditFlag, AuditLog
    from payroll.models import PayrollRun, PaySlip
    from reports.models import MonthlyReport
    
    fiscal_year = FiscalYear.get_current()
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Monthly reports summary
    monthly_reports = MonthlyReport.objects.filter(
        year=today.year,
        month=today.month
    )
    
    total_due = sum(r.mission_remittance_balance for r in monthly_reports if r.mission_remittance_balance > 0)
    overdue_reports = [r for r in monthly_reports if r.is_overdue]
    
    context = {
        # Financial Overview
        'total_contributions': Contribution.objects.filter(
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'total_expenditure': Expenditure.objects.filter(
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'net_balance': ((Contribution.objects.filter(
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0) - 
        (Expenditure.objects.filter(
            date__gte=month_start,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0)),
        
        # Monthly Reports
        'monthly_reports_count': monthly_reports.count(),
        'total_due': total_due,
        'overdue_count': len(overdue_reports),
        'overdue_amount': sum(r.mission_remittance_balance for r in overdue_reports),
        
        # Payroll
        'payroll_runs': PayrollRun.objects.filter(
            fiscal_year=fiscal_year
        ).count(),
        'total_payroll': PaySlip.objects.filter(
            payroll_run__fiscal_year=fiscal_year
        ).aggregate(total=Sum('net_pay'))['total'] or 0,
        
        # Audit
        'pending_remittances': Remittance.objects.filter(
            status__in=['pending', 'sent']
        ).count(),
        'flags_count': AuditFlag.objects.filter(status='open').count(),
        'recent_logs': AuditLog.objects.select_related('user').order_by('-timestamp')[:10],
        
        # Branch Performance
        'branches': Branch.objects.filter(is_active=True).annotate(
            contribution_total=Sum('contributions__amount'),
            expenditure_total=Sum('expenditures__amount')
        ).order_by('-contribution_total')[:10],
        
        'fiscal_year': fiscal_year,
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/auditor_dashboard.html', context)


@login_required
def pastor_dashboard(request):
    """Dashboard for Pastors."""
    from contributions.models import TitheCommission, Contribution, ContributionType
    from attendance.models import AttendanceSession, AttendanceRecord
    from members.models import Member
    from announcements.models import Announcement
    from sermons.models import Sermon
    from core.models import Visitor
    from django.db.models import Sum, Avg, Count, Q
    from datetime import timedelta
    
    user = request.user
    branch = user.branch
    
    fiscal_year = FiscalYear.get_current()
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Initialize context
    context = {
        'branch': branch,
        'total_members': 0,
        'avg_attendance': 0,
        'tithe_progress': 0,
        'commission_amount': 0,
        'commission_eligible': False,
    }
    
    if branch:
        # Get members for this branch
        total_members = Member.objects.filter(user__branch=branch, status='active').count()
        context['total_members'] = total_members
        
        # Calculate average attendance (last 4 weeks)
        four_weeks_ago = today - timedelta(weeks=4)
        from django.db.models import Count, Q
        
        # Get total sessions in the last 4 weeks
        total_sessions = AttendanceSession.objects.filter(
            branch=branch,
            date__gte=four_weeks_ago
        ).count()
        
        if total_sessions > 0 and total_members > 0:
            # Get number of sessions each member attended
            member_attendance = AttendanceRecord.objects.filter(
                session__branch=branch,
                session__date__gte=four_weeks_ago,
                status='present'
            ).values('member').annotate(
                sessions_attended=Count('id')
            )
            
            # Calculate average attendance rate across all members
            if member_attendance.exists():
                total_attendance = sum(rec['sessions_attended'] for rec in member_attendance)
                avg_attendance = (total_attendance / (total_members * total_sessions)) * 100
                context['avg_attendance'] = round(avg_attendance, 1)
        else:
            context['avg_attendance'] = 0
        
        # Calculate tithe progress for current month
        tithe_type = ContributionType.objects.filter(category='tithe', is_active=True).first()
        if tithe_type:
            monthly_tithe_target = getattr(branch, 'monthly_tithe_target', 0) or 0
            
            # Get actual tithe collected this month
            tithe_collected = Contribution.objects.filter(
                branch=branch,
                contribution_type=tithe_type,
                date__gte=month_start,
                fiscal_year=fiscal_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if monthly_tithe_target > 0:
                tithe_progress = (tithe_collected / monthly_tithe_target) * 100
                context['tithe_progress'] = round(tithe_progress, 1)
        
        # Get current month commission
        current_month_commission = TitheCommission.objects.filter(
            recipient=user,
            month=today.month,
            year=today.year
        ).first()
        
        if current_month_commission:
            context['commission_amount'] = current_month_commission.commission_amount
            context['commission_eligible'] = current_month_commission.status in ['pending', 'approved', 'paid']
        
        # Commission info for history
        context['commissions'] = TitheCommission.objects.filter(
            recipient=user,
            fiscal_year=fiscal_year
        ).order_by('-month')
        
        context['latest_commission'] = TitheCommission.objects.filter(
            recipient=user
        ).order_by('-year', '-month').first()
        
        # Recent attendance sessions
        context['recent_attendance'] = AttendanceSession.objects.filter(
            branch=branch
        ).order_by('-date')[:10]
        
        # Upcoming events (announcements and sermons)
        upcoming_events = list(Announcement.objects.filter(
            branch=branch,
            publish_date__gte=today
        ).order_by('publish_date')[:3])
        
        upcoming_sermons = Sermon.objects.filter(
            branch=branch,
            sermon_date__gte=today
        ).order_by('sermon_date')[:3]
        
        # Combine events
        all_events = []
        for event in upcoming_events:
            all_events.append({
                'title': event.title,
                'start_date': event.publish_date,
                'start_time': event.start_time,
                'type': 'announcement'
            })
        
        for sermon in upcoming_sermons:
            all_events.append({
                'title': sermon.title,
                'start_date': sermon.sermon_date,
                'start_time': sermon.time,
                'type': 'sermon'
            })
        
        # Sort by date
        all_events.sort(key=lambda x: x['start_date'])
        context['upcoming_events'] = all_events[:5]
        
        # Recent visitors (non-members who attended)
        context['recent_visitors'] = Visitor.objects.filter(
            branch=branch
        ).order_by('-first_visit_date')[:5]
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/pastor_dashboard.html', context)


@login_required
def staff_dashboard(request):
    """Dashboard for Staff members."""
    from payroll.models import PaySlip
    
    user = request.user
    
    context = {
        'recent_payslips': PaySlip.objects.filter(
            staff__user=user
        ).order_by('-payroll_run__year', '-payroll_run__month')[:6],
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/staff_dashboard.html', context)


@login_required
def member_dashboard(request):
    """Dashboard for regular Members."""
    from contributions.models import Contribution, ContributionType
    from attendance.models import AttendanceRecord, AttendanceSession
    from announcements.models import Announcement
    from sermons.models import Sermon
    from groups.models import GroupMembership
    
    user = request.user
    fiscal_year = FiscalYear.get_current()
    current_year = timezone.now().year
    
    # Calculate member-specific contributions (ONLY for this member)
    total_contributions = Contribution.objects.filter(
        member=user,
        fiscal_year=fiscal_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate tithe for this member only
    tithe_type = ContributionType.objects.filter(category='tithe', is_active=True).first()
    total_tithe = 0
    if tithe_type:
        total_tithe = Contribution.objects.filter(
            member=user,
            contribution_type=tithe_type,
            fiscal_year=fiscal_year
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent contributions for this member only
    recent_contributions = Contribution.objects.filter(
        member=user
    ).select_related('contribution_type').order_by('-date')[:10]
    
    # Calculate attendance rate for this member
    total_sessions = 0
    attended = 0
    attendance_rate = 0
    
    if user.branch:
        total_sessions = AttendanceSession.objects.filter(
            branch=user.branch,
            date__year=current_year
        ).count()
        attended = AttendanceRecord.objects.filter(
            member=user,
            status='present',
            session__date__year=current_year
        ).count()
        attendance_rate = round((attended / total_sessions * 100), 1) if total_sessions > 0 else 0
    
    # Get member's groups
    my_groups = GroupMembership.objects.filter(
        member=user,
        is_active=True
    ).select_related('group')
    
    # Announcements
    announcements = Announcement.objects.filter(
        is_published=True,
        publish_date__lte=timezone.now()
    )
    
    if user.branch:
        announcements = announcements.filter(
            Q(scope='mission') |
            Q(branch=user.branch)
        )
    else:
        announcements = announcements.filter(scope='mission')
        
    announcements = announcements.order_by('-publish_date')[:5]
    
    # Latest sermons
    latest_sermons = Sermon.objects.filter(
        is_published=True
    ).order_by('-sermon_date')[:5]
    
    # Contribution breakdown by type for this member
    contribution_by_type = Contribution.objects.filter(
        member=user,
        fiscal_year=fiscal_year
    ).values(
        'contribution_type__name', 'contribution_type__category'
    ).annotate(total=Sum('amount')).order_by('-total')
    
    context = {
        'total_contributions': total_contributions,
        'total_tithe': total_tithe,
        'attendance_rate': attendance_rate,
        'group_count': my_groups.count(),
        'recent_contributions': recent_contributions,
        'my_groups': my_groups,
        'announcements': announcements,
        'latest_sermons': latest_sermons,
        'fiscal_year': fiscal_year,
        'contribution_by_type': contribution_by_type,
    }
    
    # Add PIN change modal context
    context.update(get_pin_change_context(request))
    
    return render(request, 'core/dashboards/member_dashboard.html', context)


@login_required
def search(request):
    """Global master search."""
    query = request.GET.get('q', '')
    results = {
        'members': [], 
        'announcements': [], 
        'sermons': [],
        'groups': [],
        'branches': []
    }
    
    if query and len(query) >= 2:
        from accounts.models import User
        from announcements.models import Announcement
        from sermons.models import Sermon
        from groups.models import Group
        from core.models import Branch
        
        # Search members (if user has permission)
        if request.user.is_any_admin or request.user.is_pastor:
            results['members'] = User.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(member_id__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query)
            ).select_related('branch')[:10]
        
        # Search announcements
        results['announcements'] = Announcement.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_published=True
        )[:10]
        
        # Search sermons
        results['sermons'] = Sermon.objects.filter(
            Q(title__icontains=query) |
            Q(preacher__first_name__icontains=query) |
            Q(preacher__last_name__icontains=query) |
            Q(preacher_name__icontains=query) |
            Q(scripture_reference__icontains=query) |
            Q(summary__icontains=query)
        ).select_related('preacher')[:10]
        
        # Search groups (if user has permission)
        if request.user.is_any_admin or request.user.is_pastor:
            results['groups'] = Group.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(leader__first_name__icontains=query) |
                Q(leader__last_name__icontains=query)
            ).select_related('branch', 'leader')[:10]
        
        # Search branches (mission admin only)
        if request.user.is_mission_admin:
            results['branches'] = Branch.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(address__icontains=query) |
                Q(phone__icontains=query)
            ).select_related('district', 'district__area', 'pastor')[:10]
    
    context = {
        'query': query, 
        'results': results,
        'search_stats': {
            'total': sum(len(results[key]) for key in results),
            'has_results': any(results.values())
        }
    }
    
    return render(request, 'core/search_results.html', context)


# Administration Views

@login_required
def areas_list(request):
    """List all areas."""
    from accounts.models import User
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Handle POST actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            executive_id = request.POST.get('executive_id')
            
            if name and code:
                try:
                    area = Area.objects.create(name=name, code=code)
                    
                    # Assign executive if provided
                    if executive_id:
                        try:
                            executive = User.objects.get(pk=executive_id)
                            if executive.role == 'area_executive':
                                executive.managed_area = area
                                executive.save()
                            elif executive.role == 'pastor' and executive.pastoral_rank in ['area', 'mission']:
                                executive.managed_area = area
                                executive.save()
                        except User.DoesNotExist:
                            pass
                    
                    messages.success(request, f'Area "{name}" created successfully.')
                except Exception as e:
                    messages.error(request, f'Error creating area: {str(e)}')
            else:
                messages.error(request, 'Name and code are required.')
        
        elif action == 'edit':
            area_id = request.POST.get('area_id')
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            executive_id = request.POST.get('executive_id')
            
            if name and code and area_id:
                try:
                    area = Area.objects.get(pk=area_id)
                    area.name = name
                    area.code = code
                    
                    # Clear previous executive assignment
                    User.objects.filter(managed_area=area).update(managed_area=None)
                    
                    # Assign new executive if provided
                    if executive_id:
                        try:
                            executive = User.objects.get(pk=executive_id)
                            if executive.role == 'area_executive':
                                executive.managed_area = area
                                executive.save()
                            elif executive.role == 'pastor' and executive.pastoral_rank in ['area', 'mission']:
                                executive.managed_area = area
                                executive.save()
                        except User.DoesNotExist:
                            pass
                    
                    area.save()
                    messages.success(request, f'Area "{name}" updated successfully.')
                except Area.DoesNotExist:
                    messages.error(request, 'Area not found.')
                except Exception as e:
                    messages.error(request, f'Error updating area: {str(e)}')
            else:
                messages.error(request, 'Name, code, and area ID are required.')
        
        elif action == 'delete':
            area_id = request.POST.get('area_id')
            try:
                area = Area.objects.get(pk=area_id)
                area_name = area.name
                area.delete()
                messages.success(request, f'Area "{area_name}" deleted successfully.')
            except Area.DoesNotExist:
                messages.error(request, 'Area not found.')
            except Exception as e:
                messages.error(request, f'Error deleting area: {str(e)}')
        
        return redirect('core:areas')
    
    areas = Area.objects.annotate(
        num_districts=Count('districts', filter=Q(districts__is_active=True)),
    ).order_by('name')
    
    # Get available executives (area executives and pastors)
    executives = User.objects.filter(
        role__in=['area_executive', 'pastor']
    ).filter(
        Q(managed_area__isnull=True) | Q(pastoral_rank__in=['area', 'mission'])
    ).order_by('first_name', 'last_name')
    
    return render(request, 'core/areas.html', {
        'areas': areas,
        'executives': executives
    })


@login_required
def districts_list(request):
    """List all districts."""
    from accounts.models import User
    
    if not (request.user.is_mission_admin or request.user.is_area_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Handle POST actions
    if request.method == 'POST' and request.user.is_mission_admin:
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            area_id = request.POST.get('area_id')
            executive_id = request.POST.get('executive_id')
            
            if name and code and area_id:
                try:
                    area = Area.objects.get(pk=area_id)
                    district = District.objects.create(name=name, code=code, area=area)
                    
                    # Assign executive if provided
                    if executive_id:
                        try:
                            executive = User.objects.get(pk=executive_id)
                            if executive.role == 'district_executive':
                                executive.managed_district = district
                                executive.save()
                            elif executive.role == 'pastor' and executive.pastoral_rank in ['district', 'area', 'mission']:
                                executive.managed_district = district
                                executive.save()
                        except User.DoesNotExist:
                            pass
                    
                    messages.success(request, f'District "{name}" created successfully.')
                except Area.DoesNotExist:
                    messages.error(request, 'Area not found.')
                except Exception as e:
                    messages.error(request, f'Error creating district: {str(e)}')
            else:
                messages.error(request, 'Name, code, and area are required.')
        
        elif action == 'edit':
            district_id = request.POST.get('district_id')
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            area_id = request.POST.get('area_id')
            executive_id = request.POST.get('executive_id')
            
            try:
                district = District.objects.get(pk=district_id)
                district.name = name
                district.code = code
                if area_id:
                    district.area_id = area_id
                
                # Clear previous executive assignment
                User.objects.filter(managed_district=district).update(managed_district=None)
                
                # Assign new executive if provided
                if executive_id:
                    try:
                        executive = User.objects.get(pk=executive_id)
                        if executive.role == 'district_executive':
                            executive.managed_district = district
                            executive.save()
                        elif executive.role == 'pastor' and executive.pastoral_rank in ['district', 'area', 'mission']:
                            executive.managed_district = district
                            executive.save()
                    except User.DoesNotExist:
                        pass
                
                district.save()
                messages.success(request, f'District "{name}" updated successfully.')
            except District.DoesNotExist:
                messages.error(request, 'District not found.')
            except Exception as e:
                messages.error(request, f'Error updating district: {str(e)}')
        
        elif action == 'delete':
            district_id = request.POST.get('district_id')
            try:
                district = District.objects.get(pk=district_id)
                district_name = district.name
                district.delete()
                messages.success(request, f'District "{district_name}" deleted successfully.')
            except District.DoesNotExist:
                messages.error(request, 'District not found.')
            except Exception as e:
                messages.error(request, f'Error deleting district: {str(e)}')
        
        return redirect('core:districts')
    
    districts = District.objects.select_related('area').annotate(
        num_branches=Count('branches', filter=Q(branches__is_active=True)),
    ).order_by('area__name', 'name')
    
    # Filter by area if specified
    area_id = request.GET.get('area')
    if area_id:
        districts = districts.filter(area_id=area_id)
    
    # Get available executives (district executives and pastors)
    executives = User.objects.filter(
        role__in=['district_executive', 'pastor']
    ).filter(
        Q(managed_district__isnull=True) | Q(pastoral_rank__in=['district', 'area', 'mission'])
    ).order_by('first_name', 'last_name')
    
    return render(request, 'core/districts.html', {
        'districts': districts, 
        'areas': Area.objects.filter(is_active=True),
        'executives': executives
    })


@login_required
def branches_list(request):
    """List all branches."""
    import json
    from accounts.models import User
    
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Handle branch form actions
    if request.method == 'POST' and request.user.is_mission_admin:
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            code = request.POST.get('code', '').upper()
            district_id = request.POST.get('district')
            address = request.POST.get('address', '')
            phone = request.POST.get('phone', '')
            monthly_target = request.POST.get('monthly_tithe_target', 0)
            pastor_id = request.POST.get('pastor')
            
            try:
                district = District.objects.get(pk=district_id)
                branch = Branch.objects.create(
                    name=name,
                    code=code,
                    district=district,
                    address=address,
                    phone=phone,
                    monthly_tithe_target=monthly_target or 0,
                    pastor_id=pastor_id if pastor_id else None
                )
                messages.success(request, f'Branch "{name}" created successfully with code: {code}')
            except Exception as e:
                messages.error(request, f'Error creating branch: {str(e)}')
        
        elif action == 'edit':
            branch_id = request.POST.get('branch_id')
            name = request.POST.get('name')
            code = request.POST.get('code', '').upper()
            district_id = request.POST.get('district')
            address = request.POST.get('address', '')
            phone = request.POST.get('phone', '')
            monthly_target = request.POST.get('monthly_tithe_target', 0)
            pastor_id = request.POST.get('pastor')
            
            try:
                branch = Branch.objects.get(pk=branch_id)
                district = District.objects.get(pk=district_id)
                
                # Update branch fields
                branch.name = name
                branch.code = code
                branch.district = district
                branch.address = address
                branch.phone = phone
                branch.monthly_tithe_target = monthly_target or 0
                branch.pastor_id = pastor_id if pastor_id else None
                branch.save()
                
                messages.success(request, f'Branch "{name}" updated successfully')
            except Branch.DoesNotExist:
                messages.error(request, 'Branch not found')
            except Exception as e:
                messages.error(request, f'Error updating branch: {str(e)}')
                
        return redirect('core:branches')
    
    branches = Branch.objects.select_related('district__area', 'pastor', 'created_by', 'updated_by').order_by(
        'district__area__name', 'district__name', 'name'
    )
    
    # Add member count annotation
    from django.db.models import Count
    branches = branches.annotate(total_members=Count('users'))
    
    # Filter by user's access level
    if request.user.is_area_executive and request.user.managed_area:
        branches = branches.filter(district__area=request.user.managed_area)
    elif request.user.is_district_executive and request.user.managed_district:
        branches = branches.filter(district=request.user.managed_district)
    
    # Filter by area/district from request
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    if area_id:
        branches = branches.filter(district__area_id=area_id)
    if district_id:
        branches = branches.filter(district_id=district_id)
    
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(branches, 25)
    page = request.GET.get('page')
    branches = paginator.get_page(page)
    
    # Prepare districts JSON for JavaScript
    districts = District.objects.filter(is_active=True).select_related('area')
    districts_json = json.dumps([
        {'id': str(d.id), 'name': d.name, 'area_id': str(d.area_id)} 
        for d in districts
    ])
    
    return render(request, 'core/branches.html', {
        'branches': branches,
        'areas': Area.objects.filter(is_active=True),
        'districts': districts,
        'districts_json': districts_json,
        'pastors': User.objects.filter(role='pastor', is_active=True).order_by('first_name', 'last_name'),
    })


@login_required
def branch_detail_api(request, branch_id):
    """API endpoint to get branch details as JSON."""
    if not request.user.is_any_admin:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        branch = Branch.objects.select_related('district__area', 'pastor').get(pk=branch_id)
        data = {
            'id': str(branch.id),
            'name': branch.name,
            'code': branch.code,
            'address': branch.address,
            'phone': branch.phone,
            'monthly_tithe_target': float(branch.monthly_tithe_target),
            'district_id': str(branch.district_id),
            'area_id': str(branch.district.area_id),
            'pastor_id': str(branch.pastor_id) if branch.pastor_id else None,
        }
        return JsonResponse(data)
    except Branch.DoesNotExist:
        return JsonResponse({'error': 'Branch not found'}, status=404)


@login_required
def settings_view(request):
    """Site settings page - comprehensive system configuration."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    settings_obj = SiteSettings.get_settings()
    
    if request.method == 'POST':
        section = request.POST.get('section', 'branding')
        
        if section == 'branding':
            settings_obj.site_name = request.POST.get('site_name', settings_obj.site_name)
            settings_obj.tagline = request.POST.get('tagline', settings_obj.tagline)
            settings_obj.primary_color = request.POST.get('primary_color', settings_obj.primary_color)
            settings_obj.secondary_color = request.POST.get('secondary_color', settings_obj.secondary_color)
            settings_obj.accent_color = request.POST.get('accent_color', settings_obj.accent_color)
            settings_obj.sidebar_color = request.POST.get('sidebar_color', settings_obj.sidebar_color)
        
        elif section == 'images':
            # Logo
            if 'site_logo' in request.FILES:
                settings_obj.site_logo = request.FILES['site_logo']
            settings_obj.site_logo_url = request.POST.get('site_logo_url', settings_obj.site_logo_url)
            # Favicon
            if 'site_favicon' in request.FILES:
                settings_obj.site_favicon = request.FILES['site_favicon']
            settings_obj.site_favicon_url = request.POST.get('site_favicon_url', settings_obj.site_favicon_url)
            # Login background
            if 'login_background' in request.FILES:
                settings_obj.login_background = request.FILES['login_background']
            settings_obj.login_background_url = request.POST.get('login_background_url', settings_obj.login_background_url)
            # Dashboard banner
            if 'dashboard_banner' in request.FILES:
                settings_obj.dashboard_banner = request.FILES['dashboard_banner']
            settings_obj.dashboard_banner_url = request.POST.get('dashboard_banner_url', settings_obj.dashboard_banner_url)
            # Footer text
            settings_obj.footer_text = request.POST.get('footer_text', settings_obj.footer_text)
        
        elif section == 'contact':
            settings_obj.email = request.POST.get('email', settings_obj.email)
            settings_obj.phone = request.POST.get('phone', settings_obj.phone)
            settings_obj.alternate_phone = request.POST.get('alternate_phone', settings_obj.alternate_phone)
            settings_obj.address = request.POST.get('address', settings_obj.address)
            settings_obj.postal_address = request.POST.get('postal_address', settings_obj.postal_address)
            settings_obj.website = request.POST.get('website', settings_obj.website)
        
        elif section == 'social':
            settings_obj.facebook_url = request.POST.get('facebook_url', settings_obj.facebook_url)
            settings_obj.twitter_url = request.POST.get('twitter_url', settings_obj.twitter_url)
            settings_obj.youtube_url = request.POST.get('youtube_url', settings_obj.youtube_url)
            settings_obj.instagram_url = request.POST.get('instagram_url', settings_obj.instagram_url)
            settings_obj.whatsapp_number = request.POST.get('whatsapp_number', settings_obj.whatsapp_number)
            settings_obj.tiktok_url = request.POST.get('tiktok_url', settings_obj.tiktok_url)
        
        elif section == 'financial':
            settings_obj.currency_symbol = request.POST.get('currency_symbol', settings_obj.currency_symbol)
            settings_obj.currency_code = request.POST.get('currency_code', settings_obj.currency_code)
            settings_obj.default_tithe_target = request.POST.get('default_tithe_target', settings_obj.default_tithe_target)
            settings_obj.commission_percentage = request.POST.get('commission_percentage', settings_obj.commission_percentage)
            settings_obj.current_fiscal_year = request.POST.get('current_fiscal_year', settings_obj.current_fiscal_year)
            settings_obj.fiscal_year_start_month = request.POST.get('fiscal_year_start_month', settings_obj.fiscal_year_start_month)
        
        elif section == 'maintenance':
            settings_obj.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            settings_obj.maintenance_message = request.POST.get('maintenance_message', settings_obj.maintenance_message)
            settings_obj.maintenance_allowed_ips = request.POST.get('maintenance_allowed_ips', settings_obj.maintenance_allowed_ips)
        
        elif section == 'features':
            # General features
            settings_obj.enable_pwa = request.POST.get('enable_pwa') == 'on'
            settings_obj.enable_offline_mode = request.POST.get('enable_offline_mode') == 'on'
            settings_obj.enable_push_notifications = request.POST.get('enable_push_notifications') == 'on'
            settings_obj.enable_sms_notifications = request.POST.get('enable_sms_notifications') == 'on'
            settings_obj.enable_email_notifications = request.POST.get('enable_email_notifications') == 'on'
            # Module features
            settings_obj.enable_contributions = request.POST.get('enable_contributions') == 'on'
            settings_obj.enable_expenditure = request.POST.get('enable_expenditure') == 'on'
            settings_obj.enable_attendance = request.POST.get('enable_attendance') == 'on'
            settings_obj.enable_sermons = request.POST.get('enable_sermons') == 'on'
            settings_obj.enable_announcements = request.POST.get('enable_announcements') == 'on'
            settings_obj.enable_groups = request.POST.get('enable_groups') == 'on'
            settings_obj.enable_payroll = request.POST.get('enable_payroll') == 'on'
            settings_obj.enable_reports = request.POST.get('enable_reports') == 'on'
            settings_obj.enable_csv_import = request.POST.get('enable_csv_import') == 'on'
            # Role-specific
            settings_obj.allow_pastor_announcements = request.POST.get('allow_pastor_announcements') == 'on'
            settings_obj.allow_pastor_events = request.POST.get('allow_pastor_events') == 'on'
            settings_obj.show_pastor_contribution_panel = request.POST.get('show_pastor_contribution_panel') == 'on'
            settings_obj.allow_member_profile_edit = request.POST.get('allow_member_profile_edit') == 'on'
            settings_obj.allow_member_contribution_view = request.POST.get('allow_member_contribution_view') == 'on'
            settings_obj.allow_auditor_payroll_access = request.POST.get('allow_auditor_payroll_access') == 'on'
        
        elif section == 'security':
            settings_obj.session_timeout_minutes = request.POST.get('session_timeout_minutes', settings_obj.session_timeout_minutes)
            settings_obj.max_login_attempts = request.POST.get('max_login_attempts', settings_obj.max_login_attempts)
            settings_obj.lockout_duration_minutes = request.POST.get('lockout_duration_minutes', settings_obj.lockout_duration_minutes)
            settings_obj.require_strong_password = request.POST.get('require_strong_password') == 'on'
            settings_obj.enable_two_factor_auth = request.POST.get('enable_two_factor_auth') == 'on'
        
        elif section == 'backup':
            settings_obj.auto_backup_enabled = request.POST.get('auto_backup_enabled') == 'on'
            settings_obj.backup_frequency_days = request.POST.get('backup_frequency_days', settings_obj.backup_frequency_days)
            settings_obj.data_retention_years = request.POST.get('data_retention_years', settings_obj.data_retention_years)
        
        settings_obj.modified_by = request.user
        settings_obj.save()
        messages.success(request, f'{section.title()} settings updated successfully.')
        return redirect('core:settings')
    
    return render(request, 'core/settings.html', {'site_settings': settings_obj})


# ============ CALENDAR VIEWS ============

@login_required
def tithe_targets(request):
    """Manage monthly tithe targets for branches."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_target':
            branch_id = request.POST.get('branch_id')
            target = request.POST.get('target', 0)
            
            try:
                branch = Branch.objects.get(pk=branch_id)
                branch.monthly_tithe_target = target
                branch.save()
                messages.success(request, f'Tithe target for {branch.name} updated to GH₵{target}')
            except Branch.DoesNotExist:
                messages.error(request, 'Branch not found')
            except Exception as e:
                messages.error(request, f'Error updating target: {str(e)}')
        
        elif action == 'bulk_update':
            # Bulk update all branches with same target
            target = request.POST.get('bulk_target', 0)
            area_id = request.POST.get('bulk_area')
            district_id = request.POST.get('bulk_district')
            
            branches = Branch.objects.filter(is_active=True)
            if area_id:
                branches = branches.filter(district__area_id=area_id)
            if district_id:
                branches = branches.filter(district_id=district_id)
            
            count = branches.update(monthly_tithe_target=target)
            messages.success(request, f'Updated tithe target for {count} branches to GH₵{target}')
        
        return redirect('core:tithe_targets')
    
    # Get all branches with their targets
    branches = Branch.objects.select_related('district__area').filter(is_active=True).order_by(
        'district__area__name', 'district__name', 'name'
    )
    
    # Filter options
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    
    if area_id:
        branches = branches.filter(district__area_id=area_id)
    if district_id:
        branches = branches.filter(district_id=district_id)
    
    # Calculate statistics
    from django.db.models import Avg, Sum
    stats = branches.aggregate(
        total_target=Sum('monthly_tithe_target'),
        avg_target=Avg('monthly_tithe_target'),
        branch_count=Count('id')
    )
    
    context = {
        'branches': branches,
        'areas': Area.objects.filter(is_active=True).order_by('name'),
        'districts': District.objects.filter(is_active=True).select_related('area').order_by('name'),
        'stats': stats,
        'selected_area': area_id,
        'selected_district': district_id,
    }
    
    return render(request, 'core/tithe_targets.html', context)


@login_required
def calendar_view(request):
    """View church calendar."""
    from .calendar_models import CalendarEvent, YearlyCalendar
    from datetime import date
    import calendar as cal
    
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Get yearly calendar info
    yearly_cal = YearlyCalendar.objects.filter(year=year).first()
    
    # Get events for the month
    events = CalendarEvent.objects.filter(
        start_date__year=year,
        start_date__month=month,
        is_published=True,
        is_cancelled=False
    )
    
    # Filter by user's scope
    if not request.user.is_mission_admin:
        if request.user.branch:
            events = events.filter(
                Q(scope='mission') |
                Q(scope='branch', branch=request.user.branch) |
                Q(scope='area', area=request.user.branch.district.area) |
                Q(scope='district', branch__district=request.user.branch.district)
            )
    
    # Build calendar grid
    cal_obj = cal.Calendar(firstweekday=6)  # Sunday start
    month_days = cal_obj.monthdayscalendar(year, month)
    
    # Group events by day
    events_by_day = {}
    for event in events:
        day = event.start_date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'year': year,
        'month': month,
        'month_name': cal.month_name[month],
        'month_days': month_days,
        'events_by_day': events_by_day,
        'yearly_cal': yearly_cal,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'years': range(today.year - 1, today.year + 3),
    }
    return render(request, 'core/calendar.html', context)


@login_required
def calendar_manage(request):
    """Manage calendar events (admin only)."""
    from .calendar_models import CalendarEvent, YearlyCalendar
    from datetime import date
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:calendar')
    
    today = date.today()
    year = int(request.GET.get('year', today.year))
    
    events = CalendarEvent.objects.filter(start_date__year=year).order_by('start_date')
    yearly_cal, _ = YearlyCalendar.objects.get_or_create(year=year)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_yearly':
            yearly_cal.theme = request.POST.get('theme', '')
            yearly_cal.theme_verse = request.POST.get('theme_verse', '')
            yearly_cal.is_published = request.POST.get('is_published') == 'on'
            yearly_cal.save()
            messages.success(request, f'{year} calendar updated.')
        
        elif action == 'add_event':
            title = request.POST.get('title')
            event_type = request.POST.get('event_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date') or None
            start_time = request.POST.get('start_time') or None
            end_time = request.POST.get('end_time') or None
            location = request.POST.get('location', '')
            description = request.POST.get('description', '')
            scope = request.POST.get('scope', 'mission')
            color = request.POST.get('color', '#3B82F6')
            is_all_day = request.POST.get('is_all_day') == 'on'
            
            if title and start_date:
                CalendarEvent.objects.create(
                    title=title,
                    event_type=event_type,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    end_time=end_time,
                    location=location,
                    description=description,
                    scope=scope,
                    color=color,
                    is_all_day=is_all_day,
                    created_by=request.user,
                )
                messages.success(request, f'Event "{title}" added.')
        
        elif action == 'delete_event':
            event_id = request.POST.get('event_id')
            try:
                event = CalendarEvent.objects.get(pk=event_id)
                event.delete()
                messages.success(request, 'Event deleted.')
            except CalendarEvent.DoesNotExist:
                messages.error(request, 'Event not found.')
        
        return redirect(f'{request.path}?year={year}')
    
    context = {
        'year': year,
        'events': events,
        'yearly_cal': yearly_cal,
        'event_types': CalendarEvent.EventType.choices,
        'scopes': CalendarEvent.Scope.choices,
        'years': range(today.year - 1, today.year + 3),
    }
    return render(request, 'core/calendar_manage.html', context)


# ============ PWA VIEWS ============

def manifest_json(request):
    """Serve PWA manifest.json for iOS, Android, and Desktop."""
    from django.http import JsonResponse

    settings_obj = SiteSettings.get_settings()

    # Build absolute URLs for icons
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    base_url = f"{scheme}://{host}"

    # Use uploaded logo from settings if available, otherwise use default SVG icons
    logo_url = None
    if settings_obj and settings_obj.site_logo:
        # Check if the logo URL already includes the full URL
        logo_url = settings_obj.site_logo.url
        if not logo_url.startswith(('http://', 'https://')):
            logo_url = f"{base_url}{logo_url}"
    elif settings_obj and settings_obj.site_logo_url:
        logo_url = settings_obj.site_logo_url

    # Build icon list - prefer uploaded logo
    if logo_url:
        icons = [
            {"src": logo_url, "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": logo_url, "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": logo_url, "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
            {"src": logo_url, "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ]
        shortcut_icon = {"src": logo_url, "sizes": "192x192"}
    else:
        icons = [
            {"src": f"{base_url}/static/images/icon-192.svg", "sizes": "192x192", "type": "image/svg+xml", "purpose": "any"},
            {"src": f"{base_url}/static/images/icon-512.svg", "sizes": "512x512", "type": "image/svg+xml", "purpose": "any"},
            {"src": f"{base_url}/static/images/icon-192.svg", "sizes": "192x192", "type": "image/svg+xml", "purpose": "maskable"},
            {"src": f"{base_url}/static/images/icon-512.svg", "sizes": "512x512", "type": "image/svg+xml", "purpose": "maskable"},
        ]
        shortcut_icon = {"src": f"{base_url}/static/images/icon-192.svg", "sizes": "192x192"}

    manifest = {
        "id": "/",
        "name": settings_obj.site_name or "SDSCC Church Management System",
        "short_name": settings_obj.site_name[:12] if settings_obj and settings_obj.site_name else "SDSCC",
        "description": settings_obj.tagline or "Seventh Day Sabbath Church of Christ - Church Management System",
        "start_url": "/?source=pwa",
        "scope": "/",
        "display": "standalone",
        "display_override": ["standalone", "minimal-ui"],
        "background_color": "#ffffff",
        "theme_color": settings_obj.primary_color if hasattr(settings_obj, 'primary_color') else "#1e40af",
        "orientation": "portrait-primary",
        "lang": "en",
        "dir": "ltr",
        "prefer_related_applications": False,
        "icons": icons,
        "categories": ["productivity", "utilities", "business"],
        "shortcuts": [
            {
                "name": "Dashboard",
                "short_name": "Home",
                "url": "/?source=pwa",
                "description": "Go to your dashboard",
                "icons": [shortcut_icon]
            },
            {
                "name": "Announcements",
                "short_name": "News",
                "url": "/announcements/?source=pwa",
                "description": "View church announcements",
                "icons": [shortcut_icon]
            },
            {
                "name": "Members",
                "short_name": "Members",
                "url": "/members/?source=pwa",
                "description": "View church members",
                "icons": [shortcut_icon]
            }
        ],
        "related_applications": [],
        "handle_links": "preferred",
        "launch_handler": {
            "client_mode": ["navigate-existing", "auto"]
        }
    }

    response = JsonResponse(manifest)
    response['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
    return response


def service_worker(request):
    """Serve PWA service worker."""
    from django.http import HttpResponse

    sw_content = '''
const CACHE_NAME = 'sdscc-v2';
const OFFLINE_URL = '/offline/';

const STATIC_ASSETS = [
    '/offline/',
    '/static/css/output.css',
    '/static/images/icon-192.svg',
    '/static/images/icon-512.svg',
];

// Install event - pre-cache essential assets
self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-caching offline page');
            return cache.addAll(STATIC_ASSETS).catch((error) => {
                console.log('[ServiceWorker] Cache addAll failed:', error);
                // Cache assets individually as fallback
                return Promise.allSettled(STATIC_ASSETS.map(url =>
                    cache.add(url).catch(err => console.log('Failed to cache:', url))
                ));
            });
        })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME).map(name => {
                    console.log('[ServiceWorker] Deleting old cache:', name);
                    return caches.delete(name);
                })
            );
        }).then(() => {
            console.log('[ServiceWorker] Claiming clients');
            return self.clients.claim();
        })
    );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests and browser extensions
    if (event.request.method !== 'GET') return;
    if (event.request.url.startsWith('chrome-extension://')) return;
    if (event.request.url.includes('extension')) return;

    // Handle navigation requests (HTML pages)
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Clone and cache successful responses
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    console.log('[ServiceWorker] Fetch failed, returning offline page');
                    return caches.match(OFFLINE_URL);
                })
        );
        return;
    }

    // Handle static assets - cache first, network fallback
    if (event.request.url.includes('/static/') ||
        event.request.url.includes('fonts.googleapis.com') ||
        event.request.url.includes('fonts.gstatic.com') ||
        event.request.url.includes('cdn.jsdelivr.net')) {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) {
                    // Return cached version and update cache in background
                    fetch(event.request).then(response => {
                        if (response.status === 200) {
                            caches.open(CACHE_NAME).then(cache => {
                                cache.put(event.request, response);
                            });
                        }
                    }).catch(() => {});
                    return cachedResponse;
                }

                // Not in cache, fetch and cache
                return fetch(event.request).then((response) => {
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                });
            })
        );
        return;
    }

    // Default: network first for API and dynamic content
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});

// Listen for messages from clients
self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }
});
'''

    response = HttpResponse(sw_content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def offline_page(request):
    """Render offline page for PWA."""
    return render(request, 'core/offline.html')


# ============ NOTIFICATION VIEWS ============

@login_required
def notifications_list(request):
    """List all notifications for the current user."""
    from .models import Notification
    
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Filter by read status
    status = request.GET.get('status')
    if status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Mark as read action
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
            messages.success(request, 'All notifications marked as read.')
            return redirect('core:notifications')
        elif action == 'mark_read':
            notif_id = request.POST.get('notification_id')
            try:
                notif = notifications.get(pk=notif_id)
                notif.mark_as_read()
            except Notification.DoesNotExist:
                pass
            return redirect('core:notifications')
    
    context = {
        'notifications': notifications[:50],
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'core/notifications.html', context)


@login_required
def notifications_api(request):
    """API endpoint for notifications (for topbar dropdown)."""
    from .models import Notification
    
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]
    
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    data = {
        'unread_count': unread_count,
        'notifications': [
            {
                'id': str(n.id),
                'type': n.notification_type,
                'title': n.title,
                'message': n.message[:100],
                'link': n.link,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'time_ago': get_time_ago(n.created_at),
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)


def get_time_ago(dt):
    """Get human-readable time ago string."""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 30:
        return dt.strftime('%b %d, %Y')
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


# ============ PRAYER REQUEST VIEWS ============

@login_required
def prayer_requests(request):
    """List prayer requests with proper visibility control."""
    from .models import PrayerRequest, PrayerInteraction
    
    user = request.user
    is_admin = user.is_mission_admin or user.is_pastor or user.is_branch_executive
    
    # Handle approval action for admins
    if request.method == 'POST' and is_admin:
        action = request.POST.get('action')
        prayer_id = request.POST.get('prayer_id')
        if action == 'approve' and prayer_id:
            try:
                prayer = PrayerRequest.objects.get(pk=prayer_id)
                prayer.is_approved = True
                prayer.approved_by = user
                prayer.approved_at = timezone.now()
                prayer.save()
                messages.success(request, 'Prayer request approved and now visible to members.')
            except PrayerRequest.DoesNotExist:
                pass
            return redirect('core:prayer_requests')
    
    # Build queryset based on user role
    if user.is_mission_admin:
        # Mission admin sees all
        prayers = PrayerRequest.objects.all()
    elif user.is_area_executive:
        # Area exec sees area-wide and mission-wide requests
        prayers = PrayerRequest.objects.filter(
            Q(branch__district__area=user.managed_area) |
            Q(visibility_scope='mission', is_approved=True)
        )
    elif user.is_district_executive:
        # District exec sees district-wide and above
        prayers = PrayerRequest.objects.filter(
            Q(branch__district=user.managed_district) |
            Q(visibility_scope__in=['area', 'mission'], is_approved=True)
        )
    elif user.is_pastor or user.is_branch_executive:
        # Branch admin/pastor sees all in their branch (for approval) + approved wider scope
        prayers = PrayerRequest.objects.filter(
            Q(branch=user.branch) |
            Q(visibility_scope__in=['district', 'area', 'mission'], is_approved=True)
        )
    else:
        # Regular members see:
        # 1. Their own requests (always)
        # 2. Approved branch-level requests from their branch
        # 3. Approved wider-scope requests
        prayers = PrayerRequest.objects.filter(
            Q(requester=user) |
            Q(branch=user.branch, visibility_scope='branch', is_approved=True) |
            Q(visibility_scope__in=['district', 'area', 'mission'], is_approved=True)
        )
    
    prayers = prayers.select_related('requester', 'branch', 'approved_by').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        prayers = prayers.filter(status=status)
    
    # Filter by approval status for admins
    approval_filter = request.GET.get('approval')
    if is_admin and approval_filter == 'pending':
        prayers = prayers.filter(is_approved=False)
    elif is_admin and approval_filter == 'approved':
        prayers = prayers.filter(is_approved=True)
    
    # Get user's prayer interactions
    user_prayers = PrayerInteraction.objects.filter(user=user).values_list('prayer_request_id', flat=True)
    
    # Count pending approvals for admins
    pending_count = 0
    if is_admin:
        if user.is_mission_admin:
            pending_count = PrayerRequest.objects.filter(is_approved=False).count()
        elif user.branch:
            pending_count = PrayerRequest.objects.filter(branch=user.branch, is_approved=False).count()
    
    context = {
        'prayers': prayers.distinct()[:50],
        'user_prayers': list(user_prayers),
        'status_choices': PrayerRequest.Status.choices,
        'is_admin': is_admin,
        'pending_count': pending_count,
    }
    return render(request, 'core/prayer_requests.html', context)


@login_required
def prayer_request_add(request):
    """Add a new prayer request."""
    from .models import PrayerRequest
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        visibility_scope = request.POST.get('visibility_scope', 'branch')
        
        if title and description:
            PrayerRequest.objects.create(
                requester=request.user,
                branch=request.user.branch,
                title=title,
                description=description,
                visibility_scope=visibility_scope,
                is_approved=False  # Requires admin approval
            )
            messages.success(request, 'Prayer request submitted! It will be visible to others once approved by a pastor or admin.')
            return redirect('core:prayer_requests')
        else:
            messages.error(request, 'Please provide both title and description.')
    
    context = {
        'visibility_choices': PrayerRequest.VisibilityScope.choices,
    }
    return render(request, 'core/prayer_request_form.html', context)


@login_required
def prayer_request_edit(request, pk):
    """Edit a prayer request (only by the requester)."""
    from .models import PrayerRequest
    
    prayer = get_object_or_404(PrayerRequest, pk=pk)
    
    # Only allow the requester to edit
    if prayer.requester != request.user:
        messages.error(request, 'You can only edit your own prayer requests.')
        return redirect('core:prayer_requests')
    
    # Don't allow editing if already approved
    if prayer.is_approved:
        messages.warning(request, 'This prayer request cannot be edited as it has been approved.')
        return redirect('core:prayer_requests')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        visibility_scope = request.POST.get('visibility_scope', 'branch')
        
        if title and description:
            prayer.title = title
            prayer.description = description
            prayer.visibility_scope = visibility_scope
            prayer.save()
            messages.success(request, 'Prayer request updated successfully!')
            return redirect('core:prayer_requests')
        else:
            messages.error(request, 'Please provide both title and description.')
    
    context = {
        'prayer': prayer,
        'visibility_choices': PrayerRequest.VisibilityScope.choices,
    }
    return render(request, 'core/prayer_request_form.html', context)


@login_required
def prayer_request_pray(request, pk):
    """Mark that user has prayed for a request."""
    from .models import PrayerRequest, PrayerInteraction
    
    prayer = get_object_or_404(PrayerRequest, pk=pk)
    
    # Create interaction if not exists
    interaction, created = PrayerInteraction.objects.get_or_create(
        prayer_request=prayer,
        user=request.user
    )
    
    if created:
        prayer.prayer_count += 1
        prayer.save(update_fields=['prayer_count'])
        messages.success(request, 'Thank you for praying!')
    
    return redirect('core:prayer_requests')


# ============ VISITOR FOLLOW-UP VIEWS ============

@login_required
def visitors_list(request):
    """List visitors for follow-up."""
    from .models import Visitor
    
    user = request.user
    
    if not (user.is_mission_admin or user.is_pastor or user.is_branch_executive or 
            user.is_district_executive or user.is_area_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Base queryset
    if user.is_mission_admin:
        visitors = Visitor.objects.all()
    elif user.is_area_executive:
        visitors = Visitor.objects.filter(branch__district__area=user.managed_area)
    elif user.is_district_executive:
        visitors = Visitor.objects.filter(branch__district=user.managed_district)
    else:
        visitors = Visitor.objects.filter(branch=user.branch)
    
    visitors = visitors.select_related('branch', 'assigned_to', 'invited_by').order_by('-first_visit_date')
    
    # Filters
    status = request.GET.get('status')
    if status:
        visitors = visitors.filter(status=status)
    
    branch_id = request.GET.get('branch')
    if branch_id:
        visitors = visitors.filter(branch_id=branch_id)
    
    context = {
        'visitors': visitors[:100],
        'status_choices': Visitor.Status.choices,
        'branches': Branch.objects.filter(is_active=True) if user.is_mission_admin else None,
        'stats': {
            'total': visitors.count(),
            'new': visitors.filter(status='new').count(),
            'converted': visitors.filter(status='converted').count(),
            'follow_up_due': visitors.filter(next_follow_up__lte=timezone.now().date()).count(),
        }
    }
    return render(request, 'core/visitors_list.html', context)


@login_required
def visitor_add(request):
    """Add a new visitor."""
    from .models import Visitor
    
    user = request.user
    
    if not (user.is_mission_admin or user.is_pastor or user.is_branch_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        branch_id = request.POST.get('branch') or (user.branch.id if user.branch else None)
        
        if not branch_id:
            messages.error(request, 'Please select a branch.')
            return redirect('core:visitor_add')
        
        Visitor.objects.create(
            branch_id=branch_id,
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            email=request.POST.get('email', '').strip(),
            address=request.POST.get('address', '').strip(),
            first_visit_date=request.POST.get('first_visit_date') or timezone.now().date(),
            how_heard=request.POST.get('how_heard', '').strip(),
            notes=request.POST.get('notes', '').strip(),
            created_by=user
        )
        messages.success(request, 'Visitor added successfully.')
        return redirect('core:visitors')
    
    context = {
        'branches': Branch.objects.filter(is_active=True) if user.is_mission_admin else None,
    }
    return render(request, 'core/visitor_form.html', context)


@login_required
def visitor_detail(request, pk):
    """View and manage a visitor."""
    from .models import Visitor, VisitorFollowUp
    
    visitor = get_object_or_404(Visitor, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            visitor.status = request.POST.get('status')
            visitor.save(update_fields=['status'])
            messages.success(request, 'Status updated.')
        
        elif action == 'add_followup':
            VisitorFollowUp.objects.create(
                visitor=visitor,
                followed_by=request.user,
                method=request.POST.get('method'),
                notes=request.POST.get('notes'),
                follow_up_date=request.POST.get('follow_up_date') or timezone.now().date(),
                response=request.POST.get('response', ''),
                created_by=request.user
            )
            visitor.status = 'contacted'
            visitor.save(update_fields=['status'])
            messages.success(request, 'Follow-up recorded.')
        
        elif action == 'assign':
            from accounts.models import User
            assignee_id = request.POST.get('assignee')
            if assignee_id:
                visitor.assigned_to_id = assignee_id
                visitor.save(update_fields=['assigned_to'])
                messages.success(request, 'Visitor assigned.')
        
        elif action == 'schedule_followup':
            visitor.next_follow_up = request.POST.get('next_follow_up')
            visitor.status = 'follow_up'
            visitor.save(update_fields=['next_follow_up', 'status'])
            messages.success(request, 'Follow-up scheduled.')
        
        return redirect('core:visitor_detail', pk=pk)
    
    context = {
        'visitor': visitor,
        'follow_ups': visitor.follow_ups.all().order_by('-follow_up_date'),
        'status_choices': Visitor.Status.choices,
        'method_choices': VisitorFollowUp.Method.choices,
    }
    return render(request, 'core/visitor_detail.html', context)


# ============ BIRTHDAY & ANNIVERSARY VIEWS ============

@login_required
def celebrations(request):
    """View upcoming birthdays and anniversaries."""
    from .utils import get_upcoming_birthdays, get_upcoming_anniversaries
    
    user = request.user
    branch = user.branch if not user.is_mission_admin else None
    
    days = int(request.GET.get('days', 7))
    
    context = {
        'birthdays': get_upcoming_birthdays(branch, days),
        'anniversaries': get_upcoming_anniversaries(branch, days),
        'days': days,
    }
    return render(request, 'core/celebrations.html', context)


# ============ EXPORT VIEWS ============

@login_required
def export_members(request):
    """Export members to Excel with optional branch filter."""
    from .utils import export_to_excel
    from accounts.models import User
    from core.models import Branch

    if not request.user.is_any_admin:
        return HttpResponse("Access denied", status=403)

    # Get optional branch filter
    branch_id = request.GET.get('branch')

    # Get members based on user scope
    if request.user.is_mission_admin:
        members = User.objects.filter(is_active=True)
        if branch_id:
            members = members.filter(branch_id=branch_id)
    elif request.user.is_area_executive:
        members = User.objects.filter(branch__district__area=request.user.managed_area)
        if branch_id:
            members = members.filter(branch_id=branch_id)
    elif request.user.is_district_executive:
        members = User.objects.filter(branch__district=request.user.managed_district)
        if branch_id:
            members = members.filter(branch_id=branch_id)
    else:
        members = User.objects.filter(branch=request.user.branch)

    members = members.select_related('branch', 'branch__district', 'branch__district__area').order_by('branch__name', 'last_name', 'first_name')

    # Get branch name for filename
    branch_suffix = ''
    if branch_id:
        try:
            branch = Branch.objects.get(pk=branch_id)
            branch_suffix = f'_{branch.name.replace(" ", "_")}'
        except Branch.DoesNotExist:
            pass

    columns = [
        ('member_id', 'Member ID'),
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('branch.name', 'Branch'),
        ('branch.district.name', 'District'),
        ('get_role_display', 'Role'),
        ('date_of_birth', 'Date of Birth'),
        ('gender', 'Gender'),
        ('marital_status', 'Marital Status'),
        ('occupation', 'Occupation'),
        ('address', 'Address'),
        ('date_joined', 'Date Joined'),
    ]

    return export_to_excel(members, columns, f'members_export{branch_suffix}_{timezone.now().strftime("%Y%m%d")}')


@login_required
def export_contributions(request):
    """Export contributions to Excel."""
    from .utils import export_to_excel
    from contributions.models import Contribution
    
    if not (request.user.is_any_admin or request.user.is_auditor):
        return HttpResponse("Access denied", status=403)
    
    # Get contributions based on user scope
    contributions = Contribution.objects.all()
    
    if not request.user.is_mission_admin:
        if request.user.is_area_executive:
            contributions = contributions.filter(branch__district__area=request.user.managed_area)
        elif request.user.is_district_executive:
            contributions = contributions.filter(branch__district=request.user.managed_district)
        elif request.user.branch:
            contributions = contributions.filter(branch=request.user.branch)
    
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        contributions = contributions.filter(date__gte=start_date)
    if end_date:
        contributions = contributions.filter(date__lte=end_date)
    
    contributions = contributions.select_related(
        'member', 'branch', 'contribution_type'
    ).order_by('-date')[:5000]  # Limit for performance
    
    columns = [
        ('date', 'Date'),
        ('contribution_type.name', 'Type'),
        ('member.get_full_name', 'Member'),
        ('member.member_id', 'Member ID'),
        ('amount', 'Amount (GH₵)'),
        ('branch.name', 'Branch'),
        ('reference', 'Reference'),
        ('description', 'Description'),
    ]
    
    return export_to_excel(contributions, columns, f'contributions_export_{timezone.now().strftime("%Y%m%d")}')


@login_required
def import_members(request):
    """Import members from CSV."""
    from .utils import parse_csv_members
    
    user = request.user
    
    if not user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        branch_id = request.POST.get('branch')
        
        if not csv_file:
            messages.error(request, 'Please upload a CSV file.')
            return redirect('core:import_members')
        
        if not branch_id:
            messages.error(request, 'Please select a branch.')
            return redirect('core:import_members')
        
        branch = get_object_or_404(Branch, pk=branch_id)
        
        success, errors = parse_csv_members(csv_file, branch)
        
        if success:
            messages.success(request, f'Successfully imported {len(success)} members.')
        if errors:
            for error in errors[:5]:  # Show first 5 errors
                messages.error(request, f"Row {error['row']}: {error['error']}")
        
        return redirect('members:list')
    
    context = {
        'branches': Branch.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'core/import_members.html', context)


@login_required
def download_member_template(request):
    """Download CSV template for member import."""
    import csv
    from django.http import HttpResponse
    
    if not request.user.is_any_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Create CSV template
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="member_import_template.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'first_name',
        'last_name', 
        'phone',
        'email',
        'date_of_birth',
        'gender',
        'address',
        'occupation',
        'marital_status',
        'baptism_date',
        'membership_date'
    ])
    
    # Write sample data
    writer.writerow([
        'John',
        'Doe',
        '0241234567',
        'john.doe@example.com',
        '1990-05-15',
        'M',
        '123 Main Street, Accra, Ghana',
        'Teacher',
        'Married',
        '2010-06-12',
        '2010-06-15'
    ])
    
    writer.writerow([
        'Jane',
        'Smith',
        '0209876543',
        'jane.smith@example.com',
        '1985-03-20',
        'F',
        '456 Oak Avenue, Kumasi, Ghana',
        'Nurse',
        'Single',
        '2015-09-10',
        '2015-09-15'
    ])
    
    return response


@login_required
def my_statement(request):
    """Generate contribution statement for current user."""
    from .utils import generate_contribution_statement
    
    year = request.GET.get('year', timezone.now().year)
    
    return generate_contribution_statement(request.user, int(year))


# ============ DATA BACKUP VIEW ============

@login_required
def data_backup(request):
    """Admin data backup and restore utility."""
    import json
    from django.core import serializers
    from django.db import transaction
    
    # Import all models needed for backup
    from accounts.models import User
    from contributions.models import Contribution, ContributionType, Remittance
    from expenditure.models import Expenditure, ExpenditureCategory
    from attendance.models import AttendanceSession, AttendanceRecord
    from members.models import Member
    from groups.models import Group, GroupMembership
    from announcements.models import Announcement
    from payroll.models import StaffPayrollProfile, PayrollRun, PaySlip
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action', 'backup')
        
        if action == 'backup':
            backup_type = request.POST.get('backup_type', 'full')
            
            backup_data = {
                'backup_version': '2.0',
                'backup_type': backup_type,
                'generated_at': timezone.now().isoformat(),
                'generated_by': request.user.get_full_name(),
            }
            
            # Always include structure data
            backup_data['site_settings'] = json.loads(serializers.serialize('json', SiteSettings.objects.all()))
            backup_data['areas'] = json.loads(serializers.serialize('json', Area.objects.all()))
            backup_data['districts'] = json.loads(serializers.serialize('json', District.objects.all()))
            backup_data['branches'] = json.loads(serializers.serialize('json', Branch.objects.all()))
            backup_data['contribution_types'] = json.loads(serializers.serialize('json', ContributionType.objects.all()))
            backup_data['expenditure_categories'] = json.loads(serializers.serialize('json', ExpenditureCategory.objects.all()))
            backup_data['groups'] = json.loads(serializers.serialize('json', Group.objects.all()))
            
            if backup_type == 'full':
                # Include all data
                backup_data['users'] = json.loads(serializers.serialize('json', User.objects.all()))
                backup_data['members'] = json.loads(serializers.serialize('json', Member.objects.all()))
                backup_data['contributions'] = json.loads(serializers.serialize('json', Contribution.objects.all()))
                backup_data['remittances'] = json.loads(serializers.serialize('json', Remittance.objects.all()))
                backup_data['expenditures'] = json.loads(serializers.serialize('json', Expenditure.objects.all()))
                backup_data['attendance_sessions'] = json.loads(serializers.serialize('json', AttendanceSession.objects.all()))
                backup_data['attendance_records'] = json.loads(serializers.serialize('json', AttendanceRecord.objects.all()))
                backup_data['announcements'] = json.loads(serializers.serialize('json', Announcement.objects.all()))
                backup_data['group_memberships'] = json.loads(serializers.serialize('json', GroupMembership.objects.all()))
                backup_data['staff_payroll'] = json.loads(serializers.serialize('json', StaffPayrollProfile.objects.all()))
                backup_data['payroll_runs'] = json.loads(serializers.serialize('json', PayrollRun.objects.all()))
                backup_data['payslips'] = json.loads(serializers.serialize('json', PaySlip.objects.all()))
            
            response = HttpResponse(
                json.dumps(backup_data, indent=2),
                content_type='application/json'
            )
            filename = f"sdscc_{backup_type}_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        elif action == 'restore':
            if 'backup_file' not in request.FILES:
                messages.error(request, 'Please select a backup file to restore.')
                return redirect('core:data_backup')
            
            try:
                backup_file = request.FILES['backup_file']
                backup_data = json.load(backup_file)
                
                # Validate backup file
                if 'backup_version' not in backup_data or 'generated_at' not in backup_data:
                    messages.error(request, 'Invalid backup file format.')
                    return redirect('core:data_backup')
                
                restore_type = request.POST.get('restore_type', 'structure')
                restored_items = []
                
                with transaction.atomic():
                    # Restore structure only
                    if 'areas' in backup_data and restore_type in ['structure', 'full']:
                        for item in serializers.deserialize('json', json.dumps(backup_data['areas'])):
                            if not Area.objects.filter(pk=item.object.pk).exists():
                                item.save()
                                restored_items.append('Areas')
                    
                    if 'districts' in backup_data and restore_type in ['structure', 'full']:
                        for item in serializers.deserialize('json', json.dumps(backup_data['districts'])):
                            if not District.objects.filter(pk=item.object.pk).exists():
                                item.save()
                                restored_items.append('Districts')
                    
                    if 'branches' in backup_data and restore_type in ['structure', 'full']:
                        for item in serializers.deserialize('json', json.dumps(backup_data['branches'])):
                            if not Branch.objects.filter(pk=item.object.pk).exists():
                                item.save()
                                restored_items.append('Branches')
                    
                    if 'contribution_types' in backup_data and restore_type in ['structure', 'full']:
                        from contributions.models import ContributionType
                        for item in serializers.deserialize('json', json.dumps(backup_data['contribution_types'])):
                            if not ContributionType.objects.filter(pk=item.object.pk).exists():
                                item.save()
                                restored_items.append('Contribution Types')
                    
                    if 'expenditure_categories' in backup_data and restore_type in ['structure', 'full']:
                        from expenditure.models import ExpenditureCategory
                        for item in serializers.deserialize('json', json.dumps(backup_data['expenditure_categories'])):
                            if not ExpenditureCategory.objects.filter(pk=item.object.pk).exists():
                                item.save()
                                restored_items.append('Expenditure Categories')
                
                unique_items = list(set(restored_items))
                if unique_items:
                    messages.success(request, f'Restore completed! Restored: {", ".join(unique_items)}')
                else:
                    messages.info(request, 'No new items to restore. All items already exist.')
                    
            except json.JSONDecodeError:
                messages.error(request, 'Invalid JSON file. Please select a valid backup file.')
            except Exception as e:
                messages.error(request, f'Error during restore: {str(e)}')
            
            return redirect('core:data_backup')
    
    # GET request - show backup page with stats
    from accounts.models import User
    from contributions.models import Contribution
    from members.models import Member
    
    context = {
        'stats': {
            'areas': Area.objects.count(),
            'districts': District.objects.count(),
            'branches': Branch.objects.count(),
            'users': User.objects.count(),
            'members': Member.objects.count(),
            'contributions': Contribution.objects.count(),
        }
    }
    return render(request, 'core/data_backup.html', context)


# ============ ERROR HANDLERS ============

@login_required
def month_close_management(request):
    """Manage month closing for all branches."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from datetime import date
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Get all months that can be closed
    from .models import MonthlyClose, FiscalYear
    fiscal_year = FiscalYear.get_current()
    
    # Get closed months
    closed_months = MonthlyClose.objects.filter(
        is_closed=True
    ).values('year', 'month').annotate(
        branch_count=Count('branch', distinct=True)
    ).order_by('-year', '-month')
    
    # Get all branches
    branches = Branch.objects.filter(is_active=True)
    total_branches = branches.count()
    
    # Check which months are fully closed
    fully_closed_months = []
    for cm in closed_months:
        if cm['branch_count'] >= total_branches:
            fully_closed_months.append(cm)
    
    # Check current month status
    current_month_closed = MonthlyClose.objects.filter(
        year=current_year,
        month=current_month,
        is_closed=True
    ).count()
    
    # Generate month names safely
    import calendar
    month_names = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        'current_year': current_year,
        'current_month': current_month,
        'current_month_name': today.strftime('%B'),
        'fully_closed_months': fully_closed_months,
        'total_branches': total_branches,
        'current_month_closed': current_month_closed,
        'months': month_names,
        'years': list(range(current_year - 2, current_year + 1)),
    }
    
    return render(request, 'core/month_close_management.html', context)


@login_required
def close_month_action(request):
    """Close a specific month."""
    if not request.user.is_mission_admin:
        return JsonResponse({'success': False, 'error': 'Access denied - Mission admin required'})
    
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))
            
            # Validate month and year
            if month < 1 or month > 12:
                return JsonResponse({'success': False, 'error': 'Invalid month'})
            if year < 2020 or year > 2030:
                return JsonResponse({'success': False, 'error': 'Invalid year'})
            
            # Import the service here to avoid potential circular imports
            try:
                from .monthly_closing import MonthlyClosingService
                from django.db import transaction
                from django.utils import timezone
                
                branches = Branch.objects.filter(is_active=True)
                
                with transaction.atomic():
                    # Mission admin close applies to ALL branches using the service
                    for branch in branches:
                        service = MonthlyClosingService(branch, month, year)
                        service.close_month(request.user)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully closed {timezone.now().strftime("%B")} {year} for all branches'
                })
                
            except ImportError as e:
                return JsonResponse({'success': False, 'error': f'Monthly closing service not available: {str(e)}'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Error during month closing: {str(e)}'})
            
        except ValueError as e:
            return JsonResponse({'success': False, 'error': f'Invalid data format: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'POST request required'})


def error_400(request, exception=None):
    """Handle 400 Bad Request errors."""
    return render(request, '400.html', status=400)


def error_403(request, exception=None):
    """Handle 403 Forbidden errors."""
    return render(request, '403.html', status=403)


def error_404(request, exception=None):
    """Handle 404 Not Found errors."""
    return render(request, '404.html', status=404)


def error_405(request, exception=None):
    """Handle 405 Method Not Allowed errors."""
    return render(request, '405.html', status=405)


def error_500(request):
    """Handle 500 Internal Server errors."""
    return render(request, '500.html', status=500)


@login_required
def archives(request):
    """View for accessing archived data."""
    return render(request, 'core/archives.html')
