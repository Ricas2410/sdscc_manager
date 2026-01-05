from django import template
from ..models import PrayerRequest

register = template.Library()

@register.filter
def can_manage_prayer(prayer, user):
    """Check if user can manage (edit/delete) this prayer request."""
    if not user or not prayer:
        return False
    return prayer.can_be_managed_by(user)

@register.filter
def can_approve_prayer(prayer, user):
    """Check if user can approve this prayer request."""
    if not user or not prayer:
        return False
    # Don't allow creators to approve their own requests
    if prayer.requester == user:
        return False
    return prayer.can_be_approved_by(user)

@register.filter
def can_pray_for_prayer(prayer, user):
    """Check if user can pray for this prayer request."""
    if not user or not prayer:
        return False
    return prayer.can_be_prayed_by(user)
