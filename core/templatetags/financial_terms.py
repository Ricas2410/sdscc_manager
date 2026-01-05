"""
Template tags for improved financial terminology
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def friendly_financial_term(value):
    """Convert technical financial terms to user-friendly terms."""
    terms_map = {
        'CASH': 'Money Held',
        'cash': 'Money Held',
        'RECEIVABLE': 'Money Owed to Us',
        'receivable': 'Money Owed to Us',
        'PAYABLE': 'Money We Owe',
        'payable': 'Money We Owe',
        'income': 'Money Received',
        'expenditure': 'Money Spent',
        'remittance': 'Money Sent',
        'contribution': 'Money Received',
        'transfer': 'Money Moved',
        'allocation': 'Money Distributed',
        'balance': 'Current Funds',
    }
    
    if value in terms_map:
        return terms_map[value]
    return value

@register.filter
def financial_amount_class(value):
    """Return CSS class based on financial amount."""
    try:
        amount = float(value)
        if amount > 0:
            return 'text-green-600'
        elif amount < 0:
            return 'text-red-600'
        return 'text-gray-600'
    except (ValueError, TypeError):
        return 'text-gray-600'

@register.simple_tag
def financial_term_tooltip(term, explanation):
    """Create a tooltip with financial term explanation."""
    return mark_safe(f'<span class="financial-term" data-tooltip="{explanation}">{term}</span>')

@register.simple_tag
def financial_help_icon(explanation):
    """Create a help icon with financial term explanation."""
    return mark_safe(f'<span class="financial-help-icon material-icons-outlined text-sm text-gray-500 ml-1 cursor-help" data-tooltip="{explanation}">help_outline</span>')
