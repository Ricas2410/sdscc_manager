"""
Expenditure Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Expenditure, ExpenditureCategory, UtilityBill, WelfarePayment, Asset


@login_required
def expenditure_categories(request):
    """Manage expenditure categories (Mission Admin only)."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    categories = ExpenditureCategory.objects.all().order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                # Generate code from name (uppercase, no spaces)
                code = name.upper().replace(' ', '_')[:20]
                # Ensure uniqueness
                original_code = code
                counter = 1
                while ExpenditureCategory.objects.filter(code=code).exists():
                    code = f"{original_code}_{counter}"
                    counter += 1
                
                ExpenditureCategory.objects.create(
                    name=name, 
                    code=code, 
                    description=description
                )
                messages.success(request, f'Category "{name}" created successfully with code "{code}".')
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            try:
                cat = ExpenditureCategory.objects.get(pk=cat_id)
                cat.delete()
                messages.success(request, 'Category deleted.')
            except ExpenditureCategory.DoesNotExist:
                messages.error(request, 'Category not found.')
        return redirect('expenditure:categories')
    
    return render(request, 'expenditure/categories.html', {'categories': categories})


@login_required
def expenditure_list(request):
    """List expenditures with hierarchical filtering."""
    from core.models import Branch, District, Area
    from django.db.models import Sum, Q
    
    expenditures = Expenditure.objects.select_related(
        'branch', 'branch__district', 'branch__district__area', 
        'category', 'created_by', 'approved_by'
    )
    
    # Role-based filtering
    if request.user.is_branch_executive and request.user.branch:
        expenditures = expenditures.filter(branch=request.user.branch)
    elif request.user.is_district_executive and request.user.managed_district:
        expenditures = expenditures.filter(branch__district=request.user.managed_district)
    elif request.user.is_area_executive and request.user.managed_area:
        expenditures = expenditures.filter(branch__district__area=request.user.managed_area)
    
    # Hierarchical filters from request
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    
    if area_id:
        expenditures = expenditures.filter(branch__district__area_id=area_id)
    if district_id:
        expenditures = expenditures.filter(branch__district_id=district_id)
    if branch_id:
        expenditures = expenditures.filter(branch_id=branch_id)
    if category_id:
        expenditures = expenditures.filter(category_id=category_id)
    if status:
        expenditures = expenditures.filter(status=status)
    
    # Calculate totals
    totals = expenditures.aggregate(
        total_amount=Sum('amount'),
        approved_amount=Sum('amount', filter=Q(status='approved') | Q(status='paid')),
        pending_amount=Sum('amount', filter=Q(status='pending'))
    )
    
    # Pagination
    paginator = Paginator(expenditures.order_by('-date'), 25)
    page = request.GET.get('page')
    expenditures = paginator.get_page(page)
    
    # Get filter options
    areas = Area.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).select_related('area').order_by('name')
    branches = Branch.objects.filter(is_active=True).select_related('district', 'district__area').order_by('name')
    categories = ExpenditureCategory.objects.filter(is_active=True).order_by('name')
    
    # Filter options based on user role
    if request.user.is_area_executive and request.user.managed_area:
        areas = areas.filter(id=request.user.managed_area_id)
        districts = districts.filter(area=request.user.managed_area)
        branches = branches.filter(district__area=request.user.managed_area)
    elif request.user.is_district_executive and request.user.managed_district:
        districts = districts.filter(id=request.user.managed_district_id)
        branches = branches.filter(district=request.user.managed_district)
        areas = Area.objects.none()
    elif request.user.is_branch_executive and request.user.branch:
        branches = branches.filter(id=request.user.branch_id)
        districts = District.objects.none()
        areas = Area.objects.none()
    
    context = {
        'expenditures': expenditures,
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'categories': categories,
        'totals': totals,
        'selected_area': area_id,
        'selected_district': district_id,
        'selected_branch': branch_id,
        'selected_category': category_id,
        'selected_status': status,
    }
    
    return render(request, 'expenditure/expenditure_list.html', context)


@login_required
def expenditure_add(request):
    """Add an expenditure."""
    from datetime import date
    from core.models import Branch
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        exp_date = request.POST.get('date')
        description = request.POST.get('description', '')
        reference = request.POST.get('reference', '')
        branch_id = request.POST.get('branch', request.user.branch_id)
        
        try:
            from core.models import FiscalYear
            branch = Branch.objects.get(pk=branch_id) if branch_id else request.user.branch
            fiscal_year = FiscalYear.get_current()
            
            expenditure = Expenditure.objects.create(
                category_id=category_id,
                amount=amount,
                date=exp_date,
                title=description[:200] if description else 'Expenditure',
                description=description,
                reference_number=reference,
                branch=branch,
                fiscal_year=fiscal_year,
                created_by=request.user
            )
            messages.success(request, f'Expenditure of GH₵{amount} recorded successfully.')
            return redirect('expenditure:list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    categories = ExpenditureCategory.objects.all()
    branches = Branch.objects.filter(is_active=True)
    
    if request.user.branch and not request.user.is_mission_admin:
        branches = branches.filter(pk=request.user.branch_id)
    
    context = {
        'categories': categories,
        'branches': branches,
        'today': date.today().isoformat(),
    }
    return render(request, 'expenditure/expenditure_form.html', context)


@login_required
def expenditure_detail(request, expenditure_id):
    """View expenditure detail."""
    expenditure = get_object_or_404(Expenditure, pk=expenditure_id)
    return render(request, 'expenditure/expenditure_detail.html', {'expenditure': expenditure})


@login_required
def utility_bills(request):
    """Manage utility bills."""
    from core.models import Branch, FiscalYear
    from django.db.models import Sum
    from datetime import date
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            utility_type = request.POST.get('utility_type')
            amount = request.POST.get('amount')
            bill_date = request.POST.get('date')
            provider = request.POST.get('provider', '')
            month = request.POST.get('month', date.today().month)
            year = request.POST.get('year', date.today().year)
            notes = request.POST.get('notes', '')
            branch_id = request.POST.get('branch', request.user.branch_id)
            
            try:
                branch = Branch.objects.get(pk=branch_id) if branch_id else request.user.branch
                fiscal_year = FiscalYear.get_current()
                
                UtilityBill.objects.create(
                    branch=branch,
                    fiscal_year=fiscal_year,
                    utility_type=utility_type,
                    month=month,
                    year=year,
                    amount=amount,
                    provider=provider,
                    notes=notes,
                    created_by=request.user
                )
                messages.success(request, f'Utility bill of GH₵{amount} recorded successfully.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        
        elif action == 'mark_paid':
            bill_id = request.POST.get('bill_id')
            payment_date = request.POST.get('payment_date')
            payment_ref = request.POST.get('payment_reference', '')
            
            try:
                bill = UtilityBill.objects.get(pk=bill_id)
                bill.is_paid = True
                bill.payment_date = payment_date
                bill.payment_reference = payment_ref
                bill.save()
                messages.success(request, 'Bill marked as paid.')
            except UtilityBill.DoesNotExist:
                messages.error(request, 'Bill not found.')
        
        return redirect('expenditure:utilities')
    
    bills = UtilityBill.objects.select_related('branch', 'fiscal_year')
    
    if request.user.is_branch_executive and request.user.branch:
        bills = bills.filter(branch=request.user.branch)
    
    # Filter by utility type
    utility_type = request.GET.get('type')
    if utility_type:
        bills = bills.filter(utility_type=utility_type)
    
    # Calculate summaries
    today = date.today()
    current_month_bills = bills.filter(month=today.month, year=today.year)
    
    summaries = {
        'electricity': current_month_bills.filter(utility_type='electricity').aggregate(total=Sum('amount'))['total'] or 0,
        'water': current_month_bills.filter(utility_type='water').aggregate(total=Sum('amount'))['total'] or 0,
        'internet': current_month_bills.filter(utility_type='internet').aggregate(total=Sum('amount'))['total'] or 0,
        'total': current_month_bills.aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    bills = bills.order_by('-year', '-month', '-created_at')
    
    context = {
        'bills': bills,
        'summaries': summaries,
        'branches': Branch.objects.filter(is_active=True) if request.user.is_mission_admin else Branch.objects.filter(pk=request.user.branch_id),
    }
    
    return render(request, 'expenditure/utility_bills.html', context)


@login_required
def welfare_payments(request):
    """Manage welfare payments."""
    from core.models import Branch, FiscalYear
    from accounts.models import User
    from django.db.models import Sum
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            welfare_type = request.POST.get('welfare_type')
            amount = request.POST.get('amount')
            payment_date = request.POST.get('date')
            recipient_id = request.POST.get('recipient')
            recipient_name = request.POST.get('recipient_name', '')
            description = request.POST.get('description', '')
            branch_id = request.POST.get('branch', request.user.branch_id)
            
            try:
                branch = Branch.objects.get(pk=branch_id) if branch_id else request.user.branch
                fiscal_year = FiscalYear.get_current()
                
                payment = WelfarePayment.objects.create(
                    branch=branch,
                    fiscal_year=fiscal_year,
                    welfare_type=welfare_type,
                    date=payment_date,
                    amount=amount,
                    recipient_id=recipient_id if recipient_id else None,
                    recipient_name=recipient_name,
                    description=description,
                    approved_by=request.user,
                    created_by=request.user
                )
                messages.success(request, f'Welfare payment of GH₵{amount} recorded successfully.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        
        return redirect('expenditure:welfare')
    
    payments = WelfarePayment.objects.select_related('branch', 'recipient', 'approved_by')
    
    if request.user.is_branch_executive and request.user.branch:
        payments = payments.filter(branch=request.user.branch)
    
    # Filter by welfare type
    welfare_type = request.GET.get('type')
    if welfare_type:
        payments = payments.filter(welfare_type=welfare_type)
    
    payments = payments.order_by('-date')
    
    # Calculate total
    total_welfare = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'payments': payments,
        'total_welfare': total_welfare,
        'branches': Branch.objects.filter(is_active=True) if request.user.is_mission_admin else Branch.objects.filter(pk=request.user.branch_id),
        'members': User.objects.filter(role='member', is_active=True).select_related('branch') if request.user.branch else User.objects.none(),
    }
    
    return render(request, 'expenditure/welfare_payments.html', context)


@login_required
def assets_list(request):
    """List and manage assets."""
    from core.models import Branch
    from django.db.models import Sum, Count
    
    if not request.user.can_manage_finances:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            category = request.POST.get('category')
            quantity = request.POST.get('quantity', 1)
            purchase_price = request.POST.get('purchase_price', 0)
            purchase_date = request.POST.get('purchase_date')
            vendor = request.POST.get('vendor', '')
            description = request.POST.get('description', '')
            branch_id = request.POST.get('branch', request.user.branch_id)
            level = 'branch' if branch_id else 'mission'
            
            try:
                branch = Branch.objects.get(pk=branch_id) if branch_id else None
                
                Asset.objects.create(
                    name=name,
                    category=category,
                    level=level,
                    branch=branch,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    current_value=purchase_price,
                    purchase_date=purchase_date,
                    vendor=vendor,
                    description=description,
                    created_by=request.user
                )
                messages.success(request, f'Asset "{name}" added successfully.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        
        return redirect('expenditure:assets')
    
    assets = Asset.objects.select_related('branch')
    
    if request.user.is_branch_executive and request.user.branch:
        assets = assets.filter(branch=request.user.branch)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        assets = assets.filter(category=category)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        assets = assets.filter(status=status)
    
    assets = assets.order_by('-created_at')
    
    # Calculate statistics
    stats = assets.aggregate(
        total_value=Sum('current_value'),
        total_purchase=Sum('purchase_price'),
        total_assets=Count('id')
    )
    
    context = {
        'assets': assets,
        'stats': stats,
        'branches': Branch.objects.filter(is_active=True) if request.user.is_mission_admin else Branch.objects.filter(pk=request.user.branch_id),
    }
    
    return render(request, 'expenditure/assets_list.html', context)
