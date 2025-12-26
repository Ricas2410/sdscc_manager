#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdscc.settings')
django.setup()

from core.models import SiteSettings
from accounts.models import User

# Create site settings
settings = SiteSettings.objects.create(
    site_name='SDSCC Church Management System',
    currency_symbol='GH₵',
    currency_code='GHS'
)

# Create mission admin user
admin_user = User.objects.create_user(
    member_id='ADMIN001',
    email='admin@sdscc.fly.dev',
    password='Asare@2017',
    role='mission_admin',
    is_staff=True,
    is_superuser=True
)

print('✅ Admin user created successfully!')
print('Member ID: ADMIN001')
print('Password: Asare@2017')
print('Database: Supabase (Fresh)')
print('Login at: https://sdscc.fly.dev/accounts/login/')
