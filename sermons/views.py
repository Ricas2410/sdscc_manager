"""
Sermons Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Sermon, SermonCategory


@login_required
def sermon_list(request):
    """List sermons."""
    sermons = Sermon.objects.filter(is_published=True).select_related('category', 'preacher', 'branch')
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        sermons = sermons.filter(category__slug=category)
    
    # Search
    query = request.GET.get('q')
    if query:
        sermons = sermons.filter(title__icontains=query)
    
    categories = SermonCategory.objects.all()
    
    return render(request, 'sermons/sermon_list.html', {'sermons': sermons, 'categories': categories})


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
                branch=request.user.branch,
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
    sermon = get_object_or_404(Sermon, pk=sermon_id)
    
    # Increment view count
    sermon.view_count += 1
    sermon.save(update_fields=['view_count'])
    
    return render(request, 'sermons/sermon_detail.html', {'sermon': sermon})


@login_required
def sermon_by_slug(request, slug):
    """View sermon by slug."""
    sermon = get_object_or_404(Sermon, slug=slug, is_published=True)
    return sermon_detail(request, sermon.pk)
