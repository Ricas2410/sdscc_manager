"""
Announcements Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import Announcement, Event


@login_required
def announcement_list(request):
    """List announcements."""
    announcements = Announcement.objects.filter(
        is_published=True,
        publish_date__lte=timezone.now()
    )
    
    # Filter by user's scope
    user = request.user
    if user.branch:
        # For branch users, show:
        # 1. Mission-wide announcements
        # 2. Branch announcements for their branch (if branch is set)
        # 3. District announcements for their district (if district is set)
        # 4. Area announcements for their area (if area is set)
        branch_condition = Q(scope='branch') & (Q(branch=user.branch) | Q(branch__isnull=True))
        
        announcements = announcements.filter(
            Q(scope='mission') |
            branch_condition
        )
        
        if user.branch.district:
            announcements = announcements | announcements.filter(
                Q(scope='district', district=user.branch.district)
            )
            
            if user.branch.district.area:
                announcements = announcements | announcements.filter(
                    Q(scope='area', area=user.branch.district.area)
                )
                
        # Remove duplicates and order by publish date
        announcements = announcements.distinct().order_by('-publish_date')
    
    return render(request, 'announcements/announcement_list.html', {'announcements': announcements})


@login_required
def announcement_add(request):
    """Add announcement."""
    from core.models import Branch, District, Area
    from datetime import date
    
    if not (request.user.is_any_admin or request.user.role == request.user.Role.PASTOR):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        from django.utils import timezone
        
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        scope = request.POST.get('scope', 'branch')
        
        # Handle publish date - default to now if not provided
        publish_date_str = request.POST.get('publish_date')
        if publish_date_str:
            try:
                publish_date = timezone.make_aware(
                    datetime.strptime(publish_date_str, '%Y-%m-%d %H:%M')
                )
            except (ValueError, TypeError):
                publish_date = timezone.now()
        else:
            publish_date = timezone.now()
            
        # Handle expiry date (optional)
        expiry_date = None
        expiry_date_str = request.POST.get('expiry_date')
        if expiry_date_str:
            try:
                expiry_date = timezone.make_aware(
                    datetime.strptime(expiry_date_str, '%Y-%m-%d %H:%M')
                )
            except (ValueError, TypeError):
                pass
                
        priority = request.POST.get('priority', 'normal')
        branch_id = request.POST.get('branch')
        
        try:
            # If scope is branch, ensure branch is set
            if scope == 'branch' and not branch_id and request.user.branch:
                branch_id = str(request.user.branch.id)
                
            announcement = Announcement.objects.create(
                title=title,
                content=content,
                scope=scope,
                publish_date=publish_date,
                expiry_date=expiry_date if expiry_date else None,
                priority=priority,
                branch_id=branch_id if branch_id else None,
                created_by=request.user,
                is_published=True
            )
            messages.success(request, f'Announcement "{title}" created successfully.')
            return redirect('announcements:list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Determine branches based on user role
    branches = Branch.objects.filter(is_active=True)
    if request.user.is_branch_executive and request.user.branch:
        branches = branches.filter(pk=request.user.branch_id)
    
    context = {
        'branches': branches,
        'areas': Area.objects.filter(is_active=True),
        'today': date.today().isoformat(),
        'is_branch_admin': request.user.is_branch_executive and not request.user.is_mission_admin,
    }
    return render(request, 'announcements/announcement_form.html', context)


@login_required
def announcement_detail(request, announcement_id):
    """View announcement detail."""
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    
    # Increment view count
    announcement.view_count += 1
    announcement.save(update_fields=['view_count'])
    
    return render(request, 'announcements/announcement_detail.html', {'announcement': announcement})


@login_required
def event_list(request):
    """List events."""
    # Show all published events, ordered by date (upcoming first, then past)
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(is_published=True, start_date__gte=today).order_by('start_date', 'start_time')
    past_events = Event.objects.filter(is_published=True, start_date__lt=today).order_by('-start_date', '-start_time')
    
    # Combine upcoming events first, then past events
    events = list(upcoming_events) + list(past_events)
    
    return render(request, 'announcements/event_list.html', {'events': events})


@login_required
def event_add(request):
    """Add new event."""
    from core.models import Branch, District, Area
    from datetime import datetime, time
    
    if not (request.user.is_any_admin or request.user.role == request.user.Role.PASTOR):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date', start_date)
        end_time = request.POST.get('end_time', start_time)
        location = request.POST.get('location', '')
        scope = request.POST.get('scope', 'branch')
        branch_id = request.POST.get('branch')
        
        try:
            # Convert date and time strings to datetime objects
            start_datetime = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
            end_datetime = datetime.strptime(f"{end_date} {end_time}", '%Y-%m-%d %H:%M')
            
            event = Event.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date if end_date != start_date else None,
                start_time=start_time,
                end_time=end_time,
                location=location,
                scope=scope,
                branch_id=branch_id if branch_id else None,
                created_by=request.user,
                is_published=True
            )
            messages.success(request, f'Event "{title}" created successfully.')
            return redirect('announcements:event_list')
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    # Determine branches based on user role
    branches = Branch.objects.filter(is_active=True)
    if request.user.is_branch_executive and request.user.branch:
        branches = branches.filter(pk=request.user.branch_id)
    
    context = {
        'branches': branches,
        'areas': Area.objects.filter(is_active=True),
        'today': datetime.now().strftime('%Y-%m-%d'),
        'now': datetime.now().strftime('%H:%M'),
        'is_branch_admin': request.user.is_branch_executive and not request.user.is_mission_admin,
    }
    return render(request, 'announcements/event_form.html', context)


@login_required
def event_detail(request, event_id):
    """View event detail."""
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'announcements/event_detail.html', {'event': event})


@login_required
def event_edit(request, event_id):
    """Edit event."""
    from core.models import Branch, District, Area
    from datetime import datetime
    
    event = get_object_or_404(Event, pk=event_id)
    
    # Check permissions - creator can edit, admins can edit all
    if not (request.user.is_mission_admin or 
            (request.user == event.created_by and request.user.role != 'member')):
        messages.error(request, 'Access denied.')
        return redirect('announcements:event_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date', start_date)
        end_time = request.POST.get('end_time', start_time)
        location = request.POST.get('location', '')
        scope = request.POST.get('scope', 'branch')
        branch_id = request.POST.get('branch')
        
        try:
            event.title = title
            event.description = description
            event.start_date = start_date
            event.end_date = end_date if end_date != start_date else None
            event.start_time = start_time
            event.end_time = end_time
            event.location = location
            event.scope = scope
            event.branch_id = branch_id if branch_id else None
            event.save()
            
            messages.success(request, f'Event "{title}" updated successfully.')
            return redirect('announcements:event_list')
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    # Determine branches based on user role
    branches = Branch.objects.filter(is_active=True)
    if request.user.is_branch_executive and request.user.branch:
        branches = branches.filter(pk=request.user.branch_id)
    
    context = {
        'event': event,
        'branches': branches,
        'areas': Area.objects.filter(is_active=True),
        'start_date': event.start_date.strftime('%Y-%m-%d'),
        'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else event.start_date.strftime('%Y-%m-%d'),
        'start_time': event.start_time.strftime('%H:%M') if event.start_time else '09:00',
        'end_time': event.end_time.strftime('%H:%M') if event.end_time else '10:00',
        'is_branch_admin': request.user.is_branch_executive and not request.user.is_mission_admin,
        'is_edit': True,
    }
    return render(request, 'announcements/event_form.html', context)


@login_required
def event_delete(request, event_id):
    """Delete event."""
    event = get_object_or_404(Event, pk=event_id)
    
    # Check permissions - creator can delete, admins can delete all
    if not (request.user.is_mission_admin or 
            (request.user == event.created_by and request.user.role != 'member')):
        messages.error(request, 'Access denied.')
        return redirect('announcements:event_list')
    
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted successfully.')
        return redirect('announcements:event_list')
    
    # If GET request, redirect to list page (delete should only happen via POST)
    return redirect('announcements:event_list')


@login_required
def announcement_edit(request, announcement_id):
    """Edit announcement."""
    from core.models import Branch, District, Area
    from datetime import datetime
    
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check permissions
    if not (request.user.is_mission_admin or 
            (request.user == announcement.created_by and request.user.role != 'member')):
        messages.error(request, 'Access denied.')
        return redirect('announcements:detail', announcement_id=announcement_id)
    
    if request.method == 'POST':
        from django.utils import timezone
        
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        scope = request.POST.get('scope', 'branch')
        
        # Handle publish date - default to now if not provided
        publish_date_str = request.POST.get('publish_date')
        if publish_date_str:
            try:
                publish_date = timezone.make_aware(
                    datetime.strptime(publish_date_str, '%Y-%m-%d %H:%M')
                )
            except (ValueError, TypeError):
                publish_date = announcement.publish_date  # Keep original if invalid
        else:
            publish_date = announcement.publish_date
            
        # Handle expiry date (optional)
        expiry_date = None
        expiry_date_str = request.POST.get('expiry_date')
        if expiry_date_str:
            try:
                expiry_date = timezone.make_aware(
                    datetime.strptime(expiry_date_str, '%Y-%m-%d %H:%M')
                )
            except (ValueError, TypeError):
                pass
                
        priority = request.POST.get('priority', 'normal')
        branch_id = request.POST.get('branch')
        
        try:
            # If scope is branch, ensure branch is set
            if scope == 'branch' and not branch_id and request.user.branch:
                branch_id = str(request.user.branch.id)
                
            announcement.title = title
            announcement.content = content
            announcement.scope = scope
            announcement.publish_date = publish_date
            announcement.expiry_date = expiry_date if expiry_date else None
            announcement.priority = priority
            announcement.branch_id = branch_id if branch_id else None
            announcement.updated_by = request.user
            announcement.save()
            
            messages.success(request, f'Announcement "{title}" updated successfully.')
            return redirect('announcements:detail', announcement_id=announcement_id)
        except Exception as e:
            messages.error(request, f'Error updating announcement: {str(e)}')
    
    # Determine branches based on user role
    branches = Branch.objects.filter(is_active=True)
    if request.user.is_branch_executive and request.user.branch:
        branches = branches.filter(pk=request.user.branch_id)
    
    context = {
        'announcement': announcement,
        'branches': branches,
        'areas': Area.objects.filter(is_active=True),
        'publish_date': announcement.publish_date.strftime('%Y-%m-%d %H:%M') if announcement.publish_date else '',
        'expiry_date': announcement.expiry_date.strftime('%Y-%m-%d %H:%M') if announcement.expiry_date else '',
        'is_branch_admin': request.user.is_branch_executive and not request.user.is_mission_admin,
        'is_edit': True,
        'today': datetime.now().strftime('%Y-%m-%d'),
        'now': datetime.now().strftime('%H:%M'),
    }
    return render(request, 'announcements/announcement_form.html', context)


@login_required
def announcement_delete(request, announcement_id):
    """Delete announcement."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check permissions
    if not (request.user.is_mission_admin or 
            (request.user == announcement.created_by and request.user.role != 'member')):
        messages.error(request, 'Access denied.')
        return redirect('announcements:detail', announcement_id=announcement_id)
    
    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        messages.success(request, f'Announcement "{title}" deleted successfully.')
        return redirect('announcements:list')
    
    # If GET request, redirect to detail page (delete should only happen via POST)
    return redirect('announcements:detail', announcement_id=announcement_id)
