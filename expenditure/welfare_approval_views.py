"""
Welfare Approval Views - Complete workflow for welfare payments
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required

from expenditure.models import WelfarePayment
from core.models import Branch, Notification
from accounts.models import User


@login_required
def welfare_requests_list(request):
    """List all welfare requests with filtering."""
    if not (request.user.is_any_admin or request.user.is_branch_executive):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    from core.models import Area, District

    # Get hierarchical data for filtering
    if request.user.is_mission_admin:
        areas = Area.objects.filter(is_active=True).order_by('name')
        districts = District.objects.filter(is_active=True).select_related('area').order_by('area__name', 'name')
        branches = Branch.objects.filter(is_active=True).select_related('district__area').order_by('district__area__name', 'district__name', 'name')
        welfare_payments = WelfarePayment.objects.all()
    elif request.user.is_area_executive and request.user.managed_area:
        areas = Area.objects.filter(id=request.user.managed_area.id)
        districts = District.objects.filter(area=request.user.managed_area, is_active=True).order_by('name')
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True).order_by('district__name', 'name')
        welfare_payments = WelfarePayment.objects.filter(branch__district__area=request.user.managed_area)
    elif request.user.is_district_executive and request.user.managed_district:
        areas = Area.objects.filter(id=request.user.managed_district.area.id)
        districts = District.objects.filter(id=request.user.managed_district.id)
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True).order_by('name')
        welfare_payments = WelfarePayment.objects.filter(branch__district=request.user.managed_district)
    else:
        # Branch executive
        areas = Area.objects.filter(id=request.user.branch.district.area.id) if request.user.branch else Area.objects.none()
        districts = District.objects.filter(id=request.user.branch.district.id) if request.user.branch else District.objects.none()
        branches = Branch.objects.filter(id=request.user.branch.id) if request.user.branch else Branch.objects.none()
        welfare_payments = WelfarePayment.objects.filter(branch=request.user.branch)

    # Apply hierarchical filters
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    status = request.GET.get('status')
    welfare_type = request.GET.get('type')

    # Filter areas, districts, branches based on selection
    if area_id:
        districts = districts.filter(area_id=area_id)
        branches = branches.filter(district__area_id=area_id)
        welfare_payments = welfare_payments.filter(branch__district__area_id=area_id)

    if district_id:
        branches = branches.filter(district_id=district_id)
        welfare_payments = welfare_payments.filter(branch__district_id=district_id)

    if branch_id:
        welfare_payments = welfare_payments.filter(branch_id=branch_id)

    # Apply status filter
    if status:
        if status == 'pending':
            welfare_payments = welfare_payments.filter(approved_by__isnull=True)
        elif status == 'approved':
            welfare_payments = welfare_payments.filter(approved_by__isnull=False)

    if welfare_type:
        welfare_payments = welfare_payments.filter(welfare_type=welfare_type)

    welfare_payments = welfare_payments.select_related(
        'branch__district__area', 'recipient', 'approved_by', 'created_by'
    ).order_by('-date', '-created_at')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(welfare_payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    base_welfare_qs = WelfarePayment.objects.filter(branch__in=branches) if branches.exists() else WelfarePayment.objects.none()

    total_pending = base_welfare_qs.filter(approved_by__isnull=True).count()
    total_approved = base_welfare_qs.filter(approved_by__isnull=False).count()
    total_rejected = base_welfare_qs.filter(status='rejected').count() if hasattr(WelfarePayment, 'status') else 0
    total_paid = base_welfare_qs.filter(status='paid').count() if hasattr(WelfarePayment, 'status') else 0

    # Calculate amounts
    pending_amount = base_welfare_qs.filter(approved_by__isnull=True).aggregate(total=Sum('amount'))['total'] or 0
    approved_amount = base_welfare_qs.filter(approved_by__isnull=False).aggregate(total=Sum('amount'))['total'] or 0
    rejected_amount = base_welfare_qs.filter(status='rejected').aggregate(total=Sum('amount'))['total'] or 0 if hasattr(WelfarePayment, 'status') else 0
    paid_amount = base_welfare_qs.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0 if hasattr(WelfarePayment, 'status') else 0

    context = {
        'page_obj': page_obj,
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'welfare_types': WelfarePayment.WelfareType.choices,
        'selected_area': area_id,
        'selected_district': district_id,
        'selected_branch': branch_id,
        'selected_status': status,
        'selected_type': welfare_type,
        'summary': {
            'pending_count': total_pending,
            'approved_count': total_approved,
            'rejected_count': total_rejected,
            'paid_count': total_paid,
            'pending_amount': pending_amount,
            'approved_amount': approved_amount,
            'rejected_amount': rejected_amount,
            'paid_amount': paid_amount,
        },
        'can_approve': request.user.is_any_admin or request.user.is_branch_executive,
        'is_mission_admin': request.user.is_mission_admin,
    }

    return render(request, 'expenditure/welfare_requests_list.html', context)


@login_required
def welfare_request_detail(request, payment_id):
    """View welfare request details."""
    welfare_payment = get_object_or_404(WelfarePayment, pk=payment_id)
    
    # Check permissions
    if not request.user.is_mission_admin:
        if request.user.is_area_executive and request.user.managed_area:
            if welfare_payment.branch.district.area != request.user.managed_area:
                messages.error(request, 'Access denied.')
                return redirect('expenditure:welfare_requests')
        elif request.user.is_district_executive and request.user.managed_district:
            if welfare_payment.branch.district != request.user.managed_district:
                messages.error(request, 'Access denied.')
                return redirect('expenditure:welfare_requests')
        elif welfare_payment.branch != request.user.branch:
            messages.error(request, 'Access denied.')
            return redirect('expenditure:welfare_requests')
    
    context = {
        'welfare_payment': welfare_payment,
        'can_approve': (request.user.is_any_admin or request.user.is_branch_executive) and not welfare_payment.approved_by,
    }
    
    return render(request, 'expenditure/welfare_request_detail.html', context)


@login_required
def approve_welfare_request(request, payment_id):
    """Approve a welfare payment request."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    if not (request.user.is_any_admin or request.user.is_branch_executive):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    welfare_payment = get_object_or_404(WelfarePayment, pk=payment_id)
    
    # Check if already approved
    if welfare_payment.approved_by:
        return JsonResponse({
            'success': False,
            'message': 'This welfare request has already been approved'
        }, status=400)
    
    # Check permissions
    if not request.user.is_mission_admin:
        if request.user.is_area_executive and request.user.managed_area:
            if welfare_payment.branch.district.area != request.user.managed_area:
                return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        elif request.user.is_district_executive and request.user.managed_district:
            if welfare_payment.branch.district != request.user.managed_district:
                return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        elif welfare_payment.branch != request.user.branch:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        # Approve the welfare payment
        welfare_payment.approved_by = request.user
        welfare_payment.updated_by = request.user
        welfare_payment.save()
        
        # Create notification for requester
        if welfare_payment.created_by:
            Notification.objects.create(
                recipient=welfare_payment.created_by,
                notification_type='expenditure',
                title='Welfare Request Approved',
                message=f'Your welfare request for {welfare_payment.recipient_name} ({welfare_payment.get_welfare_type_display()}) has been approved by {request.user.get_full_name()}',
                link=f'/expenditure/welfare/{welfare_payment.id}/',
                branch=welfare_payment.branch,
                created_by=request.user
            )
        
        # Create notification for recipient if they are a member
        if welfare_payment.recipient:
            Notification.objects.create(
                recipient=welfare_payment.recipient,
                notification_type='expenditure',
                title='Welfare Payment Approved',
                message=f'A welfare payment of GH₵ {welfare_payment.amount} for {welfare_payment.get_welfare_type_display()} has been approved for you',
                link=f'/expenditure/welfare/{welfare_payment.id}/',
                branch=welfare_payment.branch,
                created_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Welfare request approved successfully',
            'approved_by': request.user.get_full_name(),
            'approved_at': timezone.now().strftime('%Y-%m-%d %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error approving welfare request: {str(e)}'
        }, status=500)


@login_required
def decline_welfare_request(request, payment_id):
    """Decline a welfare payment request."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    if not (request.user.is_any_admin or request.user.is_branch_executive):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    welfare_payment = get_object_or_404(WelfarePayment, pk=payment_id)
    
    # Check if already approved
    if welfare_payment.approved_by:
        return JsonResponse({
            'success': False,
            'message': 'Cannot decline an already approved welfare request'
        }, status=400)
    
    # Check permissions
    if not request.user.is_mission_admin:
        if request.user.is_area_executive and request.user.managed_area:
            if welfare_payment.branch.district.area != request.user.managed_area:
                return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        elif request.user.is_district_executive and request.user.managed_district:
            if welfare_payment.branch.district != request.user.managed_district:
                return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        elif welfare_payment.branch != request.user.branch:
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    decline_reason = request.POST.get('reason', '')
    if not decline_reason:
        return JsonResponse({
            'success': False,
            'message': 'Please provide a reason for declining'
        }, status=400)
    
    try:
        # Add decline reason to notes
        welfare_payment.notes = f"DECLINED by {request.user.get_full_name()} on {timezone.now().strftime('%Y-%m-%d %H:%M')}\nReason: {decline_reason}\n\n{welfare_payment.notes}"
        welfare_payment.updated_by = request.user
        welfare_payment.save()
        
        # Delete the welfare payment (or mark as declined if you prefer to keep records)
        # For now, we'll keep it but mark in notes
        
        # Create notification for requester
        if welfare_payment.created_by:
            Notification.objects.create(
                recipient=welfare_payment.created_by,
                notification_type='expenditure',
                title='Welfare Request Declined',
                message=f'Your welfare request for {welfare_payment.recipient_name} has been declined. Reason: {decline_reason}',
                link=f'/expenditure/welfare/{welfare_payment.id}/',
                branch=welfare_payment.branch,
                created_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Welfare request declined successfully',
            'declined_by': request.user.get_full_name(),
            'decline_reason': decline_reason
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error declining welfare request: {str(e)}'
        }, status=500)


@login_required
def bulk_approve_welfare(request):
    """Bulk approve multiple welfare requests."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    if not (request.user.is_any_admin or request.user.is_branch_executive):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    payment_ids = request.POST.getlist('payment_ids[]')
    if not payment_ids:
        return JsonResponse({
            'success': False,
            'message': 'No welfare requests selected'
        }, status=400)
    
    approved_count = 0
    failed_count = 0
    errors = []
    
    for payment_id in payment_ids:
        try:
            welfare_payment = WelfarePayment.objects.get(pk=payment_id)
            
            # Check permissions
            if not request.user.is_mission_admin:
                if welfare_payment.branch != request.user.branch:
                    failed_count += 1
                    errors.append(f"Access denied for payment {payment_id}")
                    continue
            
            # Skip if already approved
            if welfare_payment.approved_by:
                failed_count += 1
                errors.append(f"Payment {payment_id} already approved")
                continue
            
            # Approve
            welfare_payment.approved_by = request.user
            welfare_payment.updated_by = request.user
            welfare_payment.save()
            
            # Create notification
            if welfare_payment.created_by:
                Notification.objects.create(
                    recipient=welfare_payment.created_by,
                    notification_type='expenditure',
                    title='Welfare Request Approved',
                    message=f'Welfare request for {welfare_payment.recipient_name} approved',
                    link=f'/expenditure/welfare/{welfare_payment.id}/',
                    branch=welfare_payment.branch,
                    created_by=request.user
                )
            
            approved_count += 1
            
        except WelfarePayment.DoesNotExist:
            failed_count += 1
            errors.append(f"Payment {payment_id} not found")
        except Exception as e:
            failed_count += 1
            errors.append(f"Error with payment {payment_id}: {str(e)}")
    
    return JsonResponse({
        'success': True,
        'message': f'Approved {approved_count} welfare requests. Failed: {failed_count}',
        'approved_count': approved_count,
        'failed_count': failed_count,
        'errors': errors
    })
