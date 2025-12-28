#!/usr/bin/env python
"""
Test script to verify the fixes for:
1. Django-Q retry/timeout configuration
2. intcomma filter in templates
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdscc.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

from django.conf import settings
from django.template import Template, Context

def test_django_q_config():
    """Test Django-Q configuration"""
    print("=" * 50)
    print("Testing Django-Q Configuration...")
    print("=" * 50)
    
    # Check if Q_SETTINGS exists
    if hasattr(settings, 'Q_SETTINGS'):
        print("✓ Q_SETTINGS found in settings")
        q_settings = settings.Q_SETTINGS
        
        # Check retry and timeout values
        retry = q_settings.get('retry', 0)
        timeout = q_settings.get('timeout', 0)
        
        print(f"  - Retry: {retry} seconds")
        print(f"  - Timeout: {timeout} seconds")
        
        if retry > timeout:
            print("✓ Retry is larger than timeout (correct configuration)")
        else:
            print("✗ Retry is not larger than timeout (incorrect configuration)")
            print("  This will cause the warning: 'Retry and timeout are misconfigured'")
    else:
        print("✗ Q_SETTINGS not found in settings")
    
    print()

def test_intcomma_filter():
    """Test intcomma filter in templates"""
    print("=" * 50)
    print("Testing intcomma Filter...")
    print("=" * 50)
    
    try:
        # Test template with intcomma filter
        template_content = """
        {% load humanize %}
        {{ 1000000|intcomma }}
        {{ 12345.67|floatformat:2|intcomma }}
        """
        template = Template(template_content)
        context = Context()
        rendered = template.render(context)
        
        print("✓ Template with intcomma filter rendered successfully")
        print(f"  Rendered output: {rendered.strip()}")
        
    except TemplateSyntaxError as e:
        if "Invalid filter: 'intcomma'" in str(e):
            print("✗ intcomma filter not found")
            print("  Make sure 'django.contrib.humanize' is in INSTALLED_APPS")
            print("  And '{% load humanize %}' is at the top of your template")
        else:
            print(f"✗ Template syntax error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

def test_div_filter():
    """Test div filter in templates"""
    print("=" * 50)
    print("Testing div Filter...")
    print("=" * 50)
    
    try:
        # Test template with div filter
        template_content = """
        {% load core_tags %}
        {{ 100|div:4 }}
        {{ 100|div:0 }}
        {{ total|div:count }}
        """
        template = Template(template_content)
        context = Context({'total': 1000, 'count': 5})
        rendered = template.render(context)
        
        print("✓ Template with div filter rendered successfully")
        print(f"  Rendered output: {rendered.strip()}")
        
    except TemplateSyntaxError as e:
        if "Invalid filter: 'div'" in str(e):
            print("✗ div filter not found")
            print("  Make sure '{% load core_tags %}' is at the top of your template")
        else:
            print(f"✗ Template syntax error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

def test_mul_filter():
    """Test mul filter in templates"""
    print("=" * 50)
    print("Testing mul Filter...")
    print("=" * 50)
    
    try:
        # Test template with mul filter
        template_content = """
        {% load core_tags %}
        {{ 100|mul:4 }}
        {{ 50|mul:"0.1" }}
        {{ total|mul:count }}
        """
        template = Template(template_content)
        context = Context({'total': 100, 'count': 2})
        rendered = template.render(context)
        
        print("✓ Template with mul filter rendered successfully")
        print(f"  Rendered output: {rendered.strip()}")
        
    except TemplateSyntaxError as e:
        if "Invalid filter: 'mul'" in str(e):
            print("✗ mul filter not found")
            print("  Make sure '{% load core_tags %}' is at the top of your template")
        else:
            print(f"✗ Template syntax error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

def main():
    print("\n" + "=" * 50)
    print("SDSCC System - Bug Fix Verification")
    print("=" * 50 + "\n")
    
    test_django_q_config()
    test_intcomma_filter()
    test_div_filter()
    test_mul_filter()
    
    print("=" * 50)
    print("Test Complete!")
    print("=" * 50)
    print("=" * 50)

if __name__ == "__main__":
    main()
