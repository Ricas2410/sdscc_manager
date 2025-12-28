# Deployment script for SDSCC bug fixes
# This script ensures that the fixes are properly applied to the production environment

Write-Host "========================================" -ForegroundColor Green
Write-Host "SDSCC System - Deploying Bug Fixes" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Stop any running Django processes
Write-Host "`nStopping any running Django processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -like "*django*" -or $_.MainWindowTitle -like "*manage.py*"} | Stop-Process -Force

# Clear Python cache
Write-Host "`nClearing Python cache..." -ForegroundColor Yellow
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__"
}
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force

# Run migrations to ensure database is up to date
Write-Host "`nRunning database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

# Collect static files
Write-Host "`nCollecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Verify Django-Q configuration
Write-Host "`nVerifying Django-Q configuration..." -ForegroundColor Yellow
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdscc.settings')
django.setup()
from django.conf import settings
if hasattr(settings, 'Q_SETTINGS'):
    print('✓ Q_SETTINGS configured')
    print(f'  Retry: {settings.Q_SETTINGS.get(\"retry\")} seconds')
    print(f'  Timeout: {settings.Q_SETTINGS.get(\"timeout\")} seconds')
    if settings.Q_SETTINGS.get('retry') > settings.Q_SETTINGS.get('timeout'):
        print('✓ Configuration is correct')
    else:
        print('✗ Configuration needs fixing')
else:
    print('✗ Q_SETTINGS not found')
"

# Verify humanize app is installed
Write-Host "`nVerifying humanize app is installed..." -ForegroundColor Yellow
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdscc.settings')
django.setup()
from django.conf import settings
if 'django.contrib.humanize' in settings.INSTALLED_APPS:
    print('✓ django.contrib.humanize is installed')
else:
    print('✗ django.contrib.humanize is NOT installed')
"

# Test intcomma filter
Write-Host "`nTesting intcomma filter..." -ForegroundColor Yellow
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdscc.settings')
django.setup()
from django.template import Template, Context
try:
    template = Template('{% load humanize %}{{ 1000000|intcomma }}')
    rendered = template.render(Context({}))
    print(f'✓ intcomma filter works: {rendered.strip()}')
except Exception as e:
    print(f'✗ Error: {e}')
"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart your Django server" -ForegroundColor Cyan
Write-Host "2. The Django-Q warning should no longer appear" -ForegroundColor Cyan
Write-Host "3. The /auditor/branch-statistics/ page should work correctly" -ForegroundColor Cyan
