from django import template

register = template.Library()

print("Loading currency_filters.py")

# Note: The currency filter is now defined in core_tags.py
# This file is kept for other potential currency-related filters
