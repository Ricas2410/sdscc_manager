"""
Django settings for SDSCC Church Management System.

Seventh Day Sabbath Church of Christ - National Management System
Supports: Mission → Area → District → Branch → Members hierarchy
Production-ready for fly.io deployment with PWA support.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-48oz#lt$z8kl+7y)-f!m$mhn(#(dft=gi_kpc1wx!-^i+u9x2@')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,sdscc.fly.dev').split(',')

# CSRF Trusted Origins for fly.io
CSRF_TRUSTED_ORIGINS = [
    'https://sdscc.fly.dev',
    'https://*.fly.dev',
]
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost:8000', 'http://127.0.0.1:8000', 'https://localhost:8000', 'https://127.0.0.1:8000'])


# Application definition


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third Party Apps
    'rest_framework',
    'cloudinary_storage',
    'cloudinary',
    'corsheaders',
    'django_q',
    
    # SDSCC Apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'members.apps.MembersConfig',
    'contributions.apps.ContributionsConfig',
    'expenditure.apps.ExpenditureConfig',
    'attendance.apps.AttendanceConfig',
    'announcements.apps.AnnouncementsConfig',
    'sermons.apps.SermonsConfig',
    'groups.apps.GroupsConfig',
    'payroll.apps.PayrollConfig',
    'reports.apps.ReportsConfig',
    'auditing.apps.AuditingConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # SDSCC Custom Middleware
    'core.middleware.MaintenanceMiddleware',
    'core.middleware.ActiveUserMiddleware',
    'core.middleware.AuditLogMiddleware',
]


ROOT_URLCONF = 'sdscc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
                'core.notification_context_processor.notification_counts',
            ],
            'builtins': [
                'core.templatetags.core_tags',
            ],
        },
    },
]

WSGI_APPLICATION = 'sdscc.wsgi.application'


# Database
# SQLite for development, PostgreSQL/CockroachDB for production
# Uses DATABASE_URL environment variable in production

if os.environ.get('DATABASE_URL'):
    # Production: Use PostgreSQL/CockroachDB via DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},  # Increased to 8 for security
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Accra'  # Ghana timezone for SDSCC

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (uploads) - Cloudinary Configuration
MEDIA_URL = '/media/'  # Default fallback
MEDIA_ROOT = BASE_DIR / 'media'

# Parse CLOUDINARY_URL if provided (format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME)
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')
if CLOUDINARY_URL:
    import re
    match = re.match(r'cloudinary://(\d+):([^@]+)@(.+)', CLOUDINARY_URL)
    if match:
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': match.group(3),
            'API_KEY': match.group(1),
            'API_SECRET': match.group(2),
        }
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    if os.environ.get('CLOUDINARY_CLOUD_NAME'):
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Authentication settings
AUTHENTICATION_BACKENDS = [
    'accounts.authentication.SDSCCBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'


# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True


# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# SDSCC Custom Settings
SDSCC_SETTINGS = {
    'DEFAULT_PIN': '12345',
    'DEFAULT_PASSWORD': '12345',
    'MEMBER_ID_PREFIX': 'MEM',
    'PASTOR_ID_PREFIX': 'PST',
    'TITHE_COMMISSION_PERCENT': 10,  # Default commission percentage
    'ENABLE_PWA': True,
}


# ============ PRODUCTION SECURITY SETTINGS ============
if not DEBUG:
    # HTTPS/SSL Settings
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS Settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Other security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# ============ DJANGO-Q CONFIGURATION ============
# Configure Django-Q before it's imported
import os
# Set Django-Q configuration as environment variables to ensure early loading
# Force correct values to avoid misconfiguration
os.environ['Q_RETRY'] = '360'
os.environ['Q_TIMEOUT'] = '300'

Q_SETTINGS = {
    'retry': 360,  # 6 minutes in seconds - MUST be larger than timeout
    'timeout': 300,  # 5 minutes in seconds
    'workers': 4,
    'queue_limit': 50,
    'limit': 100,
    'save_limit': 250,
    'cpu_affinity': 1,
    'label': 'SDSCC Task Queue',
    'redis': {
        'host': os.environ.get('REDIS_HOST', 'localhost'),
        'port': int(os.environ.get('REDIS_PORT', 6379)),
        'db': 0,
        'password': os.environ.get('REDIS_PASSWORD', ''),
    }
}

# ============ LOGGING ============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'core': {  # Custom logger for our app
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
