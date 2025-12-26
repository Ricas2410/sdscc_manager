"""
Custom template tags for core app
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        if total == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0


@register.filter
def month_name(value):
    """Convert month number to month name."""
    import calendar
    try:
        month_num = int(value)
        if 1 <= month_num <= 12:
            return calendar.month_name[month_num]
        return value
    except (ValueError, TypeError):
        return value


@register.filter
def sub(value, arg):
    """Subtract arg from value, handling decimals safely."""
    try:
        if value is None and arg is None:
            return 0
        if value is None:
            return -float(arg)
        if arg is None:
            return float(value)
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Divide value by arg, handling division by zero safely."""
    try:
        if value is None or arg is None:
            return 0
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def split(value, arg):
    """Split string by delimiter."""
    try:
        if value is None:
            return []
        return str(value).split(arg)
    except (ValueError, TypeError):
        return []
