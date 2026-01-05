"""
Sermons Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Sermon, SermonCategory


@login_required
def sermon_list(request):
    """List sermons with scope filtering."""
    sermons = Sermon.objects.filter(is_published=True).select_related('category', 'preacher', 'branch')
    
    # Filter by user's scope
    user = request.user
    if user.branch:
        # For branch users, show:
        # 1. Mission-wide sermons
        # 2. Area sermons for their area (if area is set)
        # 3. District sermons for their district (if district is set)
        # 4. Branch sermons for their branch (if branch is set)
        
        # Start with mission-wide sermons
        scoped_sermons = sermons.filter(scope='mission')
        
        # Add area-level sermons
        if user.branch.district and user.branch.district.area:
            scoped_sermons = scoped_sermons | sermons.filter(
                scope='area', 
                branch__district__area=user.branch.district.area
            )
        
        # Add district-level sermons
        if user.branch.district:
            scoped_sermons = scoped_sermons | sermons.filter(
                scope='district',
                branch__district=user.branch.district
            )
        
        # Add branch-level sermons
        scoped_sermons = scoped_sermons | sermons.filter(
            scope='branch',
            branch=user.branch
        )
        
        sermons = scoped_sermons.distinct()
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        sermons = sermons.filter(category__slug=category)
    
    # Filter by preacher
    preacher_id = request.GET.get('preacher')
    if preacher_id:
        sermons = sermons.filter(preacher_id=preacher_id)
    
    # Search
    query = request.GET.get('search')
    if query:
        sermons = sermons.filter(title__icontains=query)
    
    categories = SermonCategory.objects.all()
    
    # Get unique preachers for filter dropdown
    from django.contrib.auth import get_user_model
    User = get_user_model()
    preachers = User.objects.filter(
        sermons__is_published=True
    ).distinct().order_by('first_name', 'last_name')
    
    context = {
        'sermons': sermons, 
        'categories': categories,
        'preachers': preachers
    }
    
    return render(request, 'sermons/sermon_list.html', context)


@login_required
def sermon_add(request):
    """Add a sermon."""
    from datetime import date
    from core.models import Branch
    
    if not (request.user.is_any_admin or request.user.is_pastor):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Create default categories if none exist
    if not SermonCategory.objects.exists():
        default_categories = [
            {'name': 'Sunday Service', 'slug': 'sunday-service'},
            {'name': 'Midweek Service', 'slug': 'midweek-service'},
            {'name': 'Revival', 'slug': 'revival'},
            {'name': 'Conference', 'slug': 'conference'},
            {'name': 'Youth Service', 'slug': 'youth-service'},
            {'name': 'Special Service', 'slug': 'special-service'},
            {'name': 'Bible Study', 'slug': 'bible-study'},
            {'name': 'Prayer Meeting', 'slug': 'prayer-meeting'},
        ]
        for cat in default_categories:
            SermonCategory.objects.get_or_create(name=cat['name'], defaults={'slug': cat['slug']})
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Handle category creation
        if action == 'add_category':
            cat_name = request.POST.get('category_name')
            if cat_name:
                from django.utils.text import slugify
                cat, created = SermonCategory.objects.get_or_create(
                    name=cat_name,
                    defaults={'slug': slugify(cat_name)}
                )
                if created:
                    messages.success(request, f'Category "{cat_name}" created.')
                else:
                    messages.info(request, f'Category "{cat_name}" already exists.')
            return redirect('sermons:add')
        
        title = request.POST.get('title')
        preacher_name = request.POST.get('preacher')
        sermon_date = request.POST.get('sermon_date')
        category_id = request.POST.get('category')
        scripture_reference = request.POST.get('scripture_reference', '')
        summary = request.POST.get('summary', '')
        content = request.POST.get('content', '')
        video_url = request.POST.get('video_url', '')
        scope = request.POST.get('scope', 'mission')
        branch_id = request.POST.get('branch')
        
        # Handle file uploads
        audio_file = request.FILES.get('audio_file')
        thumbnail = request.FILES.get('thumbnail')
        
        try:
            sermon = Sermon.objects.create(
                title=title,
                preacher=request.user,
                preacher_name=preacher_name,
                sermon_date=sermon_date,
                category_id=category_id if category_id else None,
                scripture_reference=scripture_reference,
                summary=summary,
                content=content,
                video_url=video_url,
                scope=scope,
                branch_id=branch_id if branch_id else (request.user.branch.id if request.user.branch else None),
                audio_file=audio_file,
                thumbnail=thumbnail,
                is_published=True
            )
            messages.success(request, f'Sermon "{title}" added successfully.')
            return redirect('sermons:list')
        except Exception as e:
            messages.error(request, f'Error adding sermon: {str(e)}')
    
    context = {
        'categories': SermonCategory.objects.all(),
        'today': date.today().isoformat(),
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'sermons/sermon_form.html', context)


@login_required
def sermon_detail(request, sermon_id):
    """View sermon detail."""
    sermon = get_object_or_404(
        Sermon.objects.select_related(
            'category', 
            'preacher', 
            'branch', 
            'branch__district', 
            'branch__district__area'
        ), 
        pk=sermon_id
    )
    
    # Check if user can view this sermon based on scope
    if not request.user.is_mission_admin and not request.user.is_auditor:
        if sermon.scope == 'branch' and sermon.branch != request.user.branch:
            messages.error(request, 'Access denied.')
            return redirect('sermons:list')
        elif sermon.scope == 'district' and sermon.branch.district != request.user.branch.district:
            messages.error(request, 'Access denied.')
            return redirect('sermons:list')
        elif sermon.scope == 'area' and (not request.user.branch.district or not request.user.branch.district.area or sermon.branch.district.area != request.user.branch.district.area):
            messages.error(request, 'Access denied.')
            return redirect('sermons:list')
    
    # Increment view count
    sermon.view_count += 1
    sermon.save(update_fields=['view_count'])
    
    return render(request, 'sermons/sermon_detail.html', {'sermon': sermon})


@login_required
def sermon_edit(request, sermon_id):
    """Edit a sermon."""
    from datetime import date
    from core.models import Branch, District, Area
    
    sermon = get_object_or_404(Sermon, pk=sermon_id)
    
    # Check permissions
    can_edit = (
        request.user.is_mission_admin or 
        request.user.is_auditor or
        (request.user == sermon.preacher) or
        (request.user.is_branch_executive and sermon.branch == request.user.branch)
    )
    
    if not can_edit:
        messages.error(request, 'Access denied.')
        return redirect('sermons:detail', sermon_id=sermon_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        preacher_name = request.POST.get('preacher')
        sermon_date = request.POST.get('sermon_date')
        category_id = request.POST.get('category')
        scripture_reference = request.POST.get('scripture_reference', '')
        summary = request.POST.get('summary', '')
        content = request.POST.get('content', '')
        video_url = request.POST.get('video_url', '')
        scope = request.POST.get('scope', 'mission')
        branch_id = request.POST.get('branch')
        
        # Handle file uploads
        audio_file = request.FILES.get('audio_file')
        thumbnail = request.FILES.get('thumbnail')
        
        try:
            sermon.title = title
            sermon.preacher_name = preacher_name
            sermon.sermon_date = sermon_date
            sermon.category_id = category_id if category_id else None
            sermon.scripture_reference = scripture_reference
            sermon.summary = summary
            sermon.content = content
            sermon.video_url = video_url
            sermon.scope = scope
            sermon.branch_id = branch_id if branch_id else (request.user.branch.id if request.user.branch else None)
            
            # Update files if new ones are uploaded
            if audio_file:
                sermon.audio_file = audio_file
            if thumbnail:
                sermon.thumbnail = thumbnail
            
            sermon.save()
            messages.success(request, f'Sermon "{title}" updated successfully.')
            return redirect('sermons:detail', sermon_id=sermon_id)
        except Exception as e:
            messages.error(request, f'Error updating sermon: {str(e)}')
    
    context = {
        'sermon': sermon,
        'categories': SermonCategory.objects.all(),
        'today': date.today().isoformat(),
        'branches': Branch.objects.filter(is_active=True),
        'areas': Area.objects.filter(is_active=True),
        'districts': District.objects.filter(is_active=True),
    }
    return render(request, 'sermons/sermon_form.html', context)


@login_required
def sermon_delete(request, sermon_id):
    """Delete a sermon."""
    sermon = get_object_or_404(Sermon, pk=sermon_id)
    
    # Check permissions
    can_delete = (
        request.user.is_mission_admin or 
        (request.user == sermon.preacher) or
        (request.user.is_branch_executive and sermon.branch == request.user.branch)
    )
    
    if not can_delete:
        messages.error(request, 'Access denied.')
        return redirect('sermons:detail', sermon_id=sermon_id)
    
    if request.method == 'POST':
        title = sermon.title
        sermon.delete()
        messages.success(request, f'Sermon "{title}" deleted successfully.')
        return redirect('sermons:list')
    
    return render(request, 'sermons/sermon_confirm_delete.html', {'sermon': sermon})


@login_required
def sermon_by_slug(request, slug):
    """View sermon by slug."""
    sermon = get_object_or_404(Sermon, slug=slug, is_published=True)
    return sermon_detail(request, sermon.pk)
