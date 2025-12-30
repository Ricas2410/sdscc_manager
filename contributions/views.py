"""
Contributions Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Contribution, ContributionType, Remittance, TitheCommission, MissionReturnsPeriod


@login_required
def contribution_list(request):
    """List contributions aggregated by branch (not individual rows)."""
    from core.models import Area, District, Branch, FiscalYear
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import date
    
    base_qs = Contribution.objects.select_related('branch', 'branch__district', 'branch__district__area')
    
    # Filter by user access
    contributions = base_qs
    if request.user.is_branch_executive and request.user.branch:
        contributions = contributions.filter(branch=request.user.branch)
    elif request.user.is_district_executive and request.user.managed_district:
        contributions = contributions.filter(branch__district=request.user.managed_district)
    elif request.user.is_area_executive and request.user.managed_area:
        contributions = contributions.filter(branch__district__area=request.user.managed_area)
    
    # Apply filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    ct_type = request.GET.get('type')
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    
    # Initialize filter options
    districts = District.objects.filter(is_active=True)
    branches = Branch.objects.filter(is_active=True).select_related('district')
    
    if from_date:
        contributions = contributions.filter(date__gte=from_date)
    if to_date:
        contributions = contributions.filter(date__lte=to_date)
    if ct_type:
        contributions = contributions.filter(contribution_type_id=ct_type)
    
    # Hierarchical filtering
    if area_id:
        contributions = contributions.filter(branch__district__area_id=area_id)
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
    
    if district_id:
        contributions = contributions.filter(branch__district_id=district_id)
        branches = branches.filter(district_id=district_id)
    
    if branch_id:
        contributions = contributions.filter(branch_id=branch_id)
    
    # Calculate statistics BEFORE aggregation
    today = date.today()
    from datetime import timedelta
    
    # Get start of week (Monday)
    week_start = today - timedelta(days=today.weekday())
    
    # Calculate stats
    today_total = contributions.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
    week_total = contributions.filter(date__gte=week_start, date__lte=today).aggregate(total=Sum('amount'))['total'] or 0
    month_total = contributions.filter(date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0
    year_total = contributions.filter(date__year=today.year).aggregate(total=Sum('amount'))['total'] or 0
    
    # Aggregate by branch (totals only)
    branch_totals = contributions.values(
        'branch__id',
        'branch__name',
        'branch__district__name',
        'branch__district__area__name'
    ).annotate(
        total_amount=Sum('amount'),
        total_count=Count('id')
    ).order_by('branch__name')
    
    # By contribution type (top 5) for overview
    by_type = contributions.values(
        'contribution_type__name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'branch_totals': branch_totals,
        'contribution_types': ContributionType.objects.filter(is_active=True),
        'areas': Area.objects.filter(is_active=True),
        'districts': districts,
        'branches': branches,
        'today_total': today_total,
        'week_total': week_total,
        'month_total': month_total,
        'year_total': year_total,
        'by_type': by_type,
    }
    
    return render(request, 'contributions/contribution_list.html', context)


@login_required
def my_contributions(request):
    """Member view - shows only their own contributions."""
    from core.models import FiscalYear
    from django.db.models import Sum
    
    user = request.user
    fiscal_year = FiscalYear.get_current()
    
    # Get only the current user's contributions
    contributions = Contribution.objects.filter(
        member=user
    ).select_related('contribution_type', 'branch').order_by('-date')
    
    # Calculate statistics
    year_total = contributions.filter(fiscal_year=fiscal_year).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # By contribution type
    by_type = contributions.filter(fiscal_year=fiscal_year).values(
        'contribution_type__name', 'contribution_type__category'
    ).annotate(total=Sum('amount')).order_by('-total')
    
    # Paginate
    paginator = Paginator(contributions, 25)
    page = request.GET.get('page')
    contributions = paginator.get_page(page)
    
    context = {
        'contributions': contributions,
        'year_total': year_total,
        'by_type': by_type,
        'fiscal_year': fiscal_year,
    }
    
    return render(request, 'contributions/my_contributions.html', context)


@login_required
def my_contribution_history(request):
    """Member view - shows contribution history by year (archived years)."""
    from core.models import FiscalYear
    from django.db.models import Sum, Count
    from datetime import date
    
    user = request.user
    selected_year = request.GET.get('year')
    
    # Get all years where member has contributions
    years_with_contributions = Contribution.objects.filter(
        member=user
    ).values('date__year').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-date__year')
    
    # Current year
    current_year = date.today().year
    
    # If year selected, show contributions for that year
    contributions = []
    year_stats = None
    if selected_year:
        selected_year = int(selected_year)
        contributions_qs = Contribution.objects.filter(
            member=user,
            date__year=selected_year
        ).select_related('contribution_type', 'branch').order_by('-date')
        
        # Calculate stats for selected year
        year_stats = contributions_qs.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # By type breakdown
        by_type = contributions_qs.values(
            'contribution_type__name', 'contribution_type__category'
        ).annotate(total=Sum('amount'), count=Count('id')).order_by('-total')
        
        # Paginate
        paginator = Paginator(contributions_qs, 50)
        page = request.GET.get('page')
        contributions = paginator.get_page(page)
        
        year_stats['by_type'] = by_type
    
    context = {
        'years': years_with_contributions,
        'current_year': current_year,
        'selected_year': selected_year,
        'contributions': contributions,
        'year_stats': year_stats,
    }
    
    return render(request, 'contributions/my_contribution_history.html', context)


@login_required
def contribution_add(request):
    """Add a contribution."""
    from accounts.models import User
    from core.models import Branch, FiscalYear
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Handle form submission
        ct_id = request.POST.get('contribution_type')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        member_id = request.POST.get('member')
        branch_id = request.POST.get('branch', request.user.branch_id)
        description = request.POST.get('description', '')
        
        try:
            contribution_type = ContributionType.objects.get(pk=ct_id)
            branch = Branch.objects.get(pk=branch_id)
            member = User.objects.get(pk=member_id) if member_id else None
            fiscal_year = FiscalYear.get_current()
            
            contribution = Contribution.objects.create(
                contribution_type=contribution_type,
                amount=amount,
                date=date,
                member=member,
                branch=branch,
                description=description,
                fiscal_year=fiscal_year,
                created_by=request.user
            )
            messages.success(request, f'Contribution of GH₵{amount} recorded successfully.')
            return redirect('contributions:list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    contribution_types = ContributionType.objects.filter(is_active=True, is_closed=False)
    branches = Branch.objects.filter(is_active=True)
    members = User.objects.filter(is_active=True)
    
    if request.user.branch and not request.user.is_mission_admin:
        members = members.filter(branch=request.user.branch)
        branches = branches.filter(pk=request.user.branch_id)
    
    from datetime import date
    context = {
        'contribution_types': contribution_types,
        'branches': branches,
        'members': members,
        'today': date.today().isoformat()
    }
    return render(request, 'contributions/contribution_form.html', context)


@login_required
def contribution_detail(request, contribution_id):
    """View contribution detail."""
    contribution = get_object_or_404(Contribution, pk=contribution_id)
    return render(request, 'contributions/contribution_detail.html', {'contribution': contribution})


@login_required
def contribution_types(request):
    """Manage contribution types (Mission Admin can add/edit)."""
    if request.method == 'POST' and request.user.is_mission_admin:
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            code = request.POST.get('code', '').upper()
            category = request.POST.get('category')
            is_individual = request.POST.get('is_individual') == '1'
            mission_pct = request.POST.get('mission_percentage', 10)
            branch_pct = request.POST.get('branch_percentage', 90)
            description = request.POST.get('description', '')
            
            if name and code and category:
                ContributionType.objects.create(
                    name=name,
                    code=code,
                    category=category,
                    is_individual=is_individual,
                    mission_percentage=mission_pct,
                    branch_percentage=branch_pct,
                    description=description
                )
                messages.success(request, f'Contribution type "{name}" created successfully.')
            else:
                messages.error(request, 'Please fill all required fields.')
                
        elif action == 'edit':
            ct_id = request.POST.get('type_id')
            try:
                ct = ContributionType.objects.get(pk=ct_id)
                ct.name = request.POST.get('name', ct.name)
                ct.code = request.POST.get('code', ct.code).upper()
                ct.category = request.POST.get('category', ct.category)
                ct.is_individual = request.POST.get('is_individual') == '1'
                ct.mission_percentage = request.POST.get('mission_percentage', ct.mission_percentage)
                ct.branch_percentage = request.POST.get('branch_percentage', ct.branch_percentage)
                ct.description = request.POST.get('description', ct.description)
                ct.save()
                messages.success(request, f'Contribution type "{ct.name}" updated successfully.')
            except ContributionType.DoesNotExist:
                messages.error(request, 'Contribution type not found.')
                
        elif action == 'delete':
            ct_id = request.POST.get('type_id')
            try:
                ct = ContributionType.objects.get(pk=ct_id)
                if ct.contributions.exists():
                    messages.error(request, f'Cannot delete "{ct.name}" - has existing contributions.')
                else:
                    name = ct.name
                    ct.delete()
                    messages.success(request, f'Contribution type "{name}" deleted.')
            except ContributionType.DoesNotExist:
                messages.error(request, 'Contribution type not found.')
                
        elif action == 'close':
            ct_id = request.POST.get('type_id')
            try:
                ct = ContributionType.objects.get(pk=ct_id)
                ct.is_closed = True
                from django.utils import timezone
                ct.closed_at = timezone.now()
                ct.save()
                messages.success(request, f'Contribution type "{ct.name}" has been closed.')
            except ContributionType.DoesNotExist:
                messages.error(request, 'Contribution type not found.')
                
        elif action == 'reopen':
            ct_id = request.POST.get('type_id')
            try:
                ct = ContributionType.objects.get(pk=ct_id)
                ct.is_closed = False
                ct.closed_at = None
                ct.save()
                messages.success(request, f'Contribution type "{ct.name}" has been reopened.')
            except ContributionType.DoesNotExist:
                messages.error(request, 'Contribution type not found.')
                
        return redirect('contributions:types')
    
    contribution_types = ContributionType.objects.all().order_by('category', 'name')
    return render(request, 'contributions/contribution_types.html', {
        'contribution_types': contribution_types,
        'active_count': contribution_types.filter(is_closed=False).count(),
        'tithe_count': contribution_types.filter(category='tithe').count(),
        'offering_count': contribution_types.filter(category='offering').count(),
    })


@login_required
def contribution_type_detail(request, type_id):
    """View contribution type details."""
    ct = get_object_or_404(ContributionType, pk=type_id)
    
    # Get contribution stats
    from django.db.models import Sum, Count
    stats = ct.contributions.aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id')
    )
    
    context = {
        'ct': ct,
        'total_amount': stats['total_amount'] or 0,
        'total_count': stats['total_count'] or 0,
    }
    return render(request, 'contributions/contribution_type_detail.html', context)


@login_required
def weekly_entry(request):
    """Weekly general contribution entry."""
    from core.models import Branch
    from datetime import date
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = request.user.branch
    if request.user.is_mission_admin:
        branch_id = request.GET.get('branch')
        if branch_id:
            branch = Branch.objects.get(pk=branch_id)
    
    if request.method == 'POST':
        # Validate that we have a branch
        if not branch:
            messages.error(request, 'Please select a branch to record contributions for.')
            return redirect('contributions:weekly_entry')

        entry_date = request.POST.get('date')
        # Get general contribution types
        general_types = ContributionType.objects.filter(is_individual=False, is_closed=False)

        from core.models import FiscalYear
        fiscal_year = FiscalYear.get_current()

        for ct in general_types:
            amount = request.POST.get(f'amount_{ct.id}')
            notes = request.POST.get(f'notes_{ct.id}', '')
            if amount and float(amount) > 0:
                Contribution.objects.create(
                    contribution_type=ct,
                    amount=amount,
                    date=entry_date,
                    branch=branch,
                    fiscal_year=fiscal_year,
                    description=notes,
                    created_by=request.user
                )

        messages.success(request, 'Weekly contributions recorded successfully.')
        return redirect('contributions:list')
    
    context = {
        'branch': branch,
        'branches': Branch.objects.filter(is_active=True) if request.user.is_mission_admin else None,
        'contribution_types': ContributionType.objects.filter(is_individual=False, is_closed=False),
        'today': date.today(),
    }
    return render(request, 'contributions/weekly_entry.html', context)


@login_required
def individual_entry(request):
    """Individual member contribution entry."""
    from core.models import Branch
    from accounts.models import User
    from datetime import date
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = request.user.branch
    contribution_type_id = request.GET.get('type')
    contribution_type = None
    
    if contribution_type_id:
        contribution_type = get_object_or_404(ContributionType, pk=contribution_type_id)
    
    if request.method == 'POST':
        entry_date = request.POST.get('date')
        ct_id = request.POST.get('contribution_type')
        contribution_type = ContributionType.objects.get(pk=ct_id)

        from core.models import FiscalYear
        fiscal_year = FiscalYear.get_current()

        # Get all members and their amounts
        members = User.objects.filter(branch=branch, is_active=True)
        for member in members:
            amount = request.POST.get(f'amount_{member.id}')
            notes = request.POST.get(f'notes_{member.id}', '')
            if amount and float(amount) > 0:
                Contribution.objects.create(
                    contribution_type=contribution_type,
                    amount=amount,
                    date=entry_date,
                    member=member,
                    branch=branch,
                    fiscal_year=fiscal_year,
                    description=notes,
                    created_by=request.user
                )

        messages.success(request, 'Individual contributions recorded successfully.')
        return redirect('contributions:list')
    
    members = User.objects.filter(branch=branch, is_active=True).order_by('first_name') if branch else []
    
    context = {
        'branch': branch,
        'contribution_types': ContributionType.objects.filter(is_individual=True, is_closed=False),
        'selected_type': contribution_type,
        'members': members,
        'today': date.today(),
    }
    return render(request, 'contributions/individual_entry.html', context)


@login_required
def remittance_list(request):
    """List remittances."""
    remittances = Remittance.objects.select_related('branch').order_by('-created_at')
    
    if request.user.is_branch_executive and request.user.branch:
        remittances = remittances.filter(branch=request.user.branch)
    
    return render(request, 'contributions/remittance_list.html', {'remittances': remittances})


@login_required
def remittance_add(request):
    """Add a remittance."""
    from core.models import Branch, FiscalYear
    from datetime import date
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = request.user.branch
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_date = request.POST.get('date') or request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method', 'mobile_money')
        reference = request.POST.get('reference', '')
        notes = request.POST.get('notes', '')
        period_month = request.POST.get('period_month')
        period_year = request.POST.get('period_year')
        
        try:
            fiscal_year = FiscalYear.get_current()
            Remittance.objects.create(
                branch=branch,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference=reference,
                notes=notes,
                period_month=period_month,
                period_year=period_year,
                fiscal_year=fiscal_year,
                submitted_by=request.user
            )
            messages.success(request, f'Remittance of GH₵{amount} submitted successfully.')
            return redirect('contributions:remittances')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'branch': branch,
        'today': date.today(),
    }
    return render(request, 'contributions/remittance_form.html', context)


@login_required
def remittance_detail(request, remittance_id):
    """View remittance details."""
    remittance = get_object_or_404(Remittance, id=remittance_id)
    
    # Check permissions - mission admin or branch executive of the branch
    if not (request.user.is_mission_admin or 
            (request.user.is_branch_executive and request.user.branch == remittance.branch)):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    return render(request, 'contributions/remittance_detail.html', {'remittance': remittance})


@login_required
def my_commission(request):
    """View my commissions (for pastors)."""
    if not request.user.is_pastor:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    from django.db.models import Sum
    from decimal import Decimal
    import calendar
    from datetime import date
    
    commissions = TitheCommission.objects.filter(recipient=request.user).order_by('-year', '-month')
    
    # Add month names to commissions
    for commission in commissions:
        commission.month_name = calendar.month_name[commission.month]
    
    # Calculate totals
    total_earned = commissions.aggregate(total=Sum('commission_amount'))['total'] or Decimal('0.00')
    total_paid = commissions.filter(status='paid').aggregate(total=Sum('commission_amount'))['total'] or Decimal('0.00')
    total_pending = commissions.filter(status='pending').aggregate(total=Sum('commission_amount'))['total'] or Decimal('0.00')
    
    # Current month commission
    today = date.today()
    current_month_commission = commissions.filter(month=today.month, year=today.year).aggregate(total=Sum('commission_amount'))['total'] or Decimal('0.00')
    
    return render(request, 'contributions/my_commission.html', {
        'commissions': commissions,
        'total_earned': total_earned,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'current_month_commission': current_month_commission,
    })


@login_required
def mission_returns(request):
    """Mission Returns Dashboard - General Admin only."""
    from core.models import Branch, Area
    from django.db.models import Sum, Count, Q
    from datetime import date
    import calendar
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Get current month/year or from params
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    # Handle actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'close_month':
            from django.utils import timezone
            period, created = MissionReturnsPeriod.objects.get_or_create(
                month=selected_month, year=selected_year,
                defaults={'opened_by': request.user}
            )
            period.status = 'closed'
            period.closed_at = timezone.now()
            period.closed_by = request.user
            period.save()
            messages.success(request, f'{calendar.month_name[selected_month]} {selected_year} has been closed.')
            
        elif action == 'reopen_month':
            try:
                period = MissionReturnsPeriod.objects.get(month=selected_month, year=selected_year)
                period.status = 'open'
                period.closed_at = None
                period.closed_by = None
                period.save()
                messages.success(request, f'{calendar.month_name[selected_month]} {selected_year} has been reopened.')
            except MissionReturnsPeriod.DoesNotExist:
                pass
        
        return redirect(f"{request.path}?month={selected_month}&year={selected_year}")
    
    # Get period status
    try:
        current_period = MissionReturnsPeriod.objects.get(month=selected_month, year=selected_year)
        period_status = current_period.status
    except MissionReturnsPeriod.DoesNotExist:
        period_status = 'open'
    
    # Get all branches with their return status
    branches = Branch.objects.filter(is_active=True).select_related('district__area')
    
    # Filters
    area_filter = request.GET.get('area')
    status_filter = request.GET.get('status')
    search = request.GET.get('q')
    
    if area_filter:
        branches = branches.filter(district__area_id=area_filter)
    if search:
        branches = branches.filter(name__icontains=search)
    
    # Get remittance data for each branch
    branch_data = []
    total_due = 0
    total_paid = 0
    total_outstanding = 0
    paid_count = 0
    unpaid_count = 0
    partial_count = 0
    
    for branch in branches:
        # Calculate amount due from contributions for this month
        month_contributions = Contribution.objects.filter(
            branch=branch,
            date__month=selected_month,
            date__year=selected_year
        ).aggregate(
            total=Sum('mission_amount')
        )['total'] or 0
        
        # Get remittance for this month
        try:
            remittance = Remittance.objects.get(
                branch=branch,
                month=selected_month,
                year=selected_year
            )
            amount_paid = remittance.amount_sent
            status = remittance.status
        except Remittance.DoesNotExist:
            amount_paid = 0
            status = 'pending'
        
        outstanding = max(0, month_contributions - amount_paid)
        
        # Determine status
        if amount_paid >= month_contributions and month_contributions > 0:
            display_status = 'paid'
            paid_count += 1
        elif amount_paid > 0 and amount_paid < month_contributions:
            display_status = 'partial'
            partial_count += 1
        else:
            display_status = 'unpaid'
            unpaid_count += 1
        
        # Filter by status
        if status_filter and display_status != status_filter:
            continue
        
        branch_data.append({
            'branch': branch,
            'amount_due': month_contributions,
            'amount_paid': amount_paid,
            'outstanding': outstanding,
            'status': display_status,
        })
        
        total_due += month_contributions
        total_paid += amount_paid
        total_outstanding += outstanding
    
    # Generate years for dropdown
    years = list(range(today.year - 2, today.year + 2))
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    context = {
        'branch_data': branch_data,
        'total_branches': len(branches),
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'partial_count': partial_count,
        'total_due': total_due,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': calendar.month_name[selected_month],
        'period_status': period_status,
        'years': years,
        'months': months,
        'areas': Area.objects.all(),
    }
    return render(request, 'contributions/mission_returns.html', context)


@login_required
def mark_return_paid(request, branch_id):
    """Mark a branch's return as paid."""
    from core.models import Branch
    from django.utils import timezone
    
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    branch = get_object_or_404(Branch, pk=branch_id)
    
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', '')
        payment_reference = request.POST.get('payment_reference', '')
        notes = request.POST.get('notes', '')
        
        # Get fiscal year for the given month/year
        from core.models import FiscalYear
        fiscal_year = FiscalYear.objects.get(year=year)
        
        # Get or create remittance
        remittance, created = Remittance.objects.get_or_create(
            branch=branch,
            month=month,
            year=year,
            defaults={
                'fiscal_year': fiscal_year
            }
        )
        
        remittance.amount_sent = amount
        remittance.payment_date = timezone.now().date()
        remittance.payment_method = payment_method
        remittance.payment_reference = payment_reference
        remittance.status = 'verified'
        remittance.verified_by = request.user
        remittance.verified_at = timezone.now()
        remittance.verification_notes = notes
        remittance.save()
        
        messages.success(request, f'Payment of GH₵{amount} recorded for {branch.name}.')
        return redirect(f"/contributions/mission-returns/?month={month}&year={year}")
    
    return redirect('contributions:mission_returns')


@login_required
def download_contribution_template(request):
    """Download CSV template for contribution import."""
    import csv
    from django.http import HttpResponse
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('contributions:list')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contribution_import_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'member_id', 'contribution_type', 'amount', 'date', 'description'
    ])
    # Sample rows
    writer.writerow(['AN001', 'Tithe', '100.00', '2024-01-15', 'Monthly tithe'])
    writer.writerow(['AN002', 'Offering', '50.00', '2024-01-15', 'Sunday offering'])
    
    return response


@login_required
def contribution_import(request):
    """Import contributions from CSV file."""
    from core.models import Branch, FiscalYear
    from accounts.models import User
    import csv
    import io
    from decimal import Decimal, InvalidOperation
    from datetime import datetime
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('contributions:list')
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('contributions:import')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV file.')
            return redirect('contributions:import')
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            success_count = 0
            error_count = 0
            errors = []
            
            fiscal_year = FiscalYear.get_current()
            branch = request.user.branch
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    member_id = row.get('member_id', '').strip()
                    contribution_type_name = row.get('contribution_type', '').strip()
                    amount_str = row.get('amount', '').strip()
                    date_str = row.get('date', '').strip()
                    description = row.get('description', '').strip()
                    
                    if not member_id or not contribution_type_name or not amount_str or not date_str:
                        errors.append(f"Row {row_num}: Missing required fields")
                        error_count += 1
                        continue
                    
                    # Find member
                    member = User.objects.filter(member_id=member_id).first()
                    if not member:
                        errors.append(f"Row {row_num}: Member {member_id} not found")
                        error_count += 1
                        continue
                    
                    # Find contribution type
                    contribution_type = ContributionType.objects.filter(
                        name__iexact=contribution_type_name
                    ).first()
                    if not contribution_type:
                        errors.append(f"Row {row_num}: Contribution type '{contribution_type_name}' not found")
                        error_count += 1
                        continue
                    
                    # Parse amount
                    try:
                        amount = Decimal(amount_str)
                    except InvalidOperation:
                        errors.append(f"Row {row_num}: Invalid amount '{amount_str}'")
                        error_count += 1
                        continue
                    
                    # Parse date
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date '{date_str}' (use YYYY-MM-DD)")
                        error_count += 1
                        continue
                    
                    # Create contribution
                    Contribution.objects.create(
                        member=member,
                        contribution_type=contribution_type,
                        amount=amount,
                        date=date,
                        description=description,
                        branch=member.branch or branch,
                        fiscal_year=fiscal_year,
                        created_by=request.user,
                    )
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    error_count += 1
            
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} contributions.')
            if error_count > 0:
                messages.warning(request, f'{error_count} rows had errors.')
                for error in errors[:10]:
                    messages.error(request, error)
            
            return redirect('contributions:list')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')
            return redirect('contributions:import')
    
    # GET request
    context = {
        'contribution_types': ContributionType.objects.filter(is_active=True),
    }
    return render(request, 'contributions/contribution_import.html', context)
