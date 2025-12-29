"""
Notification Context Processor - Add notification counts to all templates
"""

from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import TextField
from django.utils import timezone
from datetime import date, timedelta

from core.models import Notification
from announcements.models import Announcement, Event


def notification_counts(request):
    """Add notification counts to template context."""
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    today = date.today()
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).count()
    
    # Unread announcements (published in last 7 days, not yet viewed)
    seven_days_ago = today - timedelta(days=7)
    
    # Get announcements user can see based on scope
    announcements_query = Q(is_published=True, publish_date__gte=seven_days_ago)
    
    if user.branch:
        # User can see mission-wide and their branch announcements
        announcements_query &= (
            Q(scope='mission') |
            (Q(scope='branch') & Q(branch=user.branch))
        )
        
        # Add district and area announcements if applicable
        if user.branch.district:
            announcements_query |= (Q(scope='district') & Q(district=user.branch.district))
            
            if user.branch.district.area:
                announcements_query |= (Q(scope='area') & Q(area=user.branch.district.area))
    else:
        # Mission-level users see all
        announcements_query &= Q(scope='mission')
    
    # Count announcements that don't have read notifications
    # Use subquery to check for read notifications
    from django.db.models import Exists, OuterRef

    unread_announcements = Announcement.objects.filter(announcements_query).exclude(
        # Exclude announcements that have been marked as read by this user
        Exists(
            Notification.objects.filter(
                recipient=user,
                notification_type='announcement',
                is_read=True,
                link=Cast(OuterRef('pk'), TextField())
            )
        )
    ).count()

    # Upcoming events (next 30 days)
    thirty_days_ahead = today + timedelta(days=30)

    events_query = Q(is_published=True, start_date__gte=today, start_date__lte=thirty_days_ahead)

    if user.branch:
        events_query &= (
            Q(scope='mission') |
            (Q(scope='branch') & Q(branch=user.branch))
        )

        if user.branch.district:
            events_query |= (Q(scope='district') & Q(district=user.branch.district))

            if user.branch.district.area:
                events_query |= (Q(scope='area') & Q(area=user.branch.district.area))
    else:
        events_query &= Q(scope='mission')

    upcoming_events = Event.objects.filter(events_query).count()

    # Pending approvals (for admins)
    pending_approvals = 0
    if user.is_any_admin:
        from contributions.models import Contribution
        from expenditure.models import WelfarePayment

        pending_contributions = Contribution.objects.filter(status='pending').count()
        pending_welfare = WelfarePayment.objects.filter(
            branch=user.branch if user.branch else None
        ).exclude(approved_by__isnull=False).count() if user.branch else 0

        pending_approvals = pending_contributions + pending_welfare

    # Birthdays this month (for branch admins and pastors)
    birthdays_this_month = 0
    if user.is_branch_executive or user.is_pastor:
        from accounts.models import User as UserModel

        if user.branch:
            birthdays_this_month = UserModel.objects.filter(
                branch=user.branch,
                is_active=True,
                date_of_birth__month=today.month
            ).count()

    return {
        'unread_notifications': unread_notifications,
        'unread_announcements': unread_announcements,
        'upcoming_events': upcoming_events,
        'pending_approvals': pending_approvals,
        'birthdays_this_month': birthdays_this_month,
        'total_notifications': unread_notifications + unread_announcements + pending_approvals,
    }
