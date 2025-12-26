"""
Assets & Inventory Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
import json
from datetime import datetime

from core.models import ChurchAsset, ChurchAssetMaintenance, ChurchAssetTransfer, Area, District, Branch
from accounts.models import User


@login_required
def assets_list(request):
    """List all assets with filtering and pagination."""
    
    # Get accessible branches based on user role
    if request.user.is_mission_admin:
        branches = Branch.objects.filter(is_active=True)
        areas = Area.objects.all()
        districts = District.objects.all()
    elif request.user.is_area_executive and request.user.managed_area:
        branches = Branch.objects.filter(district__area=request.user.managed_area, is_active=True)
        areas = Area.objects.filter(id=request.user.managed_area.id)
        districts = District.objects.filter(area=request.user.managed_area)
    elif request.user.is_district_executive and request.user.managed_district:
        branches = Branch.objects.filter(district=request.user.managed_district, is_active=True)
        areas = Area.objects.filter(districts=request.user.managed_district)
        districts = District.objects.filter(id=request.user.managed_district.id)
    elif request.user.is_branch_executive and request.user.branch:
        branches = Branch.objects.filter(id=request.user.branch.id, is_active=True)
        areas = Area.objects.filter(districts__branch=request.user.branch)
        districts = District.objects.filter(branches=request.user.branch)
    else:
        branches = Branch.objects.none()
        areas = Area.objects.none()
        districts = District.objects.none()
    
    # Start with all assets from accessible branches
    assets = ChurchAsset.objects.filter(branch__in=branches)
    
    # Apply filters
    search = request.GET.get('search')
    area_id = request.GET.get('area')
    district_id = request.GET.get('district')
    branch_id = request.GET.get('branch')
    asset_type = request.GET.get('asset_type')
    status = request.GET.get('status')
    
    if search:
        assets = assets.filter(
            Q(name__icontains=search) |
            Q(asset_id__icontains=search) |
            Q(description__icontains=search) |
            Q(serial_number__icontains=search)
        )
    
    if area_id:
        assets = assets.filter(branch__district__area_id=area_id)
        districts = districts.filter(area_id=area_id)
    
    if district_id:
        assets = assets.filter(branch__district_id=district_id)
    
    if branch_id:
        assets = assets.filter(branch_id=branch_id)
    
    if asset_type:
        assets = assets.filter(category=asset_type)
    
    if status:
        assets = assets.filter(status=status)
    
    # Order by created date (newest first)
    assets = assets.select_related('branch', 'branch__district', 'branch__district__area')
    
    # Pagination
    paginator = Paginator(assets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Handle export
    export_format = request.GET.get('export')
    if export_format in ['pdf', 'excel']:
        return export_assets(request, assets, export_format)
    
    context = {
        'assets': page_obj,
        'areas': areas,
        'districts': districts,
        'branches': branches,
        'user': request.user,
    }
    
    return render(request, 'core/assets.html', context)


@login_required
@require_http_methods(["POST"])
def asset_add(request):
    """Add a new asset."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:assets')
    
    try:
        name = request.POST.get('name')
        asset_id = request.POST.get('asset_id')
        category = request.POST.get('category')
        branch_id = request.POST.get('branch')
        status = request.POST.get('status')
        value = request.POST.get('value')
        purchase_date = request.POST.get('purchase_date')
        description = request.POST.get('description', '')
        
        # Validate required fields
        if not all([name, asset_id, category, branch_id, status, value, purchase_date]):
            return JsonResponse({'success': False, 'errors': 'All required fields must be provided'})
        
        # Check if asset_id already exists
        if ChurchAsset.objects.filter(asset_id=asset_id).exists():
            return JsonResponse({'success': False, 'errors': 'Asset ID already exists'})
        
        # Create asset
        asset = ChurchAsset.objects.create(
            name=name,
            asset_id=asset_id,
            category=category,
            branch_id=branch_id,
            status=status,
            value=value,
            purchase_value=value,  # Set purchase value same as initial value
            purchase_date=purchase_date,
            description=description,
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'message': 'Asset added successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
@require_http_methods(["POST"])
def asset_update(request, asset_id):
    """Update an existing asset."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:assets')
    
    try:
        asset = ChurchAsset.objects.get(id=asset_id)
        
        asset.name = request.POST.get('name', asset.name)
        asset.asset_id = request.POST.get('asset_id', asset.asset_id)
        asset.category = request.POST.get('category', asset.category)
        asset.branch_id = request.POST.get('branch', asset.branch_id)
        asset.status = request.POST.get('status', asset.status)
        asset.value = request.POST.get('value', asset.value)
        asset.purchase_date = request.POST.get('purchase_date', asset.purchase_date)
        asset.description = request.POST.get('description', asset.description)
        
        asset.save()
        
        return JsonResponse({'success': True, 'message': 'Asset updated successfully'})
        
    except ChurchAsset.DoesNotExist:
        return JsonResponse({'success': False, 'errors': 'Asset not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
@require_http_methods(["POST"])
def asset_delete(request):
    """Delete an asset."""
    if not request.user.is_mission_admin:
        messages.error(request, 'Access denied.')
        return redirect('core:assets')
    
    try:
        asset_id = request.POST.get('asset_id')
        asset = ChurchAsset.objects.get(id=asset_id)
        asset.delete()
        
        messages.success(request, f'Asset "{asset.name}" deleted successfully.')
        
    except ChurchAsset.DoesNotExist:
        messages.error(request, 'Asset not found.')
    except Exception as e:
        messages.error(request, f'Error deleting asset: {str(e)}')
    
    return redirect('core:assets')


@login_required
def asset_api_detail(request, asset_id):
    """API endpoint to get asset details for editing."""
    if not request.user.is_mission_admin:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        asset = ChurchAsset.objects.get(id=asset_id)
        data = {
            'id': str(asset.id),
            'name': asset.name,
            'asset_id': asset.asset_id,
            'category': asset.category,
            'branch': str(asset.branch.id),
            'status': asset.status,
            'value': float(asset.value),
            'purchase_date': asset.purchase_date.strftime('%Y-%m-%d'),
            'description': asset.description,
        }
        return JsonResponse(data)
    except ChurchAsset.DoesNotExist:
        return JsonResponse({'error': 'Asset not found'}, status=404)


def export_assets(request, assets_queryset, format_type):
    """Export assets to PDF or Excel."""
    
    # For now, return a simple CSV export (can be enhanced with proper PDF/Excel libraries)
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="assets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Asset ID', 'Name', 'Category', 'Branch', 'District', 'Area',
        'Value (GHS)', 'Purchase Date', 'Status', 'Description'
    ])
    
    for asset in assets_queryset:
        writer.writerow([
            asset.asset_id,
            asset.name,
            asset.get_category_display(),
            asset.branch.name,
            asset.branch.district.name if asset.branch.district else '',
            asset.branch.district.area.name if asset.branch.district and asset.branch.district.area else '',
            asset.value,
            asset.purchase_date.strftime('%Y-%m-%d'),
            asset.get_status_display(),
            asset.description
        ])
    
    return response
