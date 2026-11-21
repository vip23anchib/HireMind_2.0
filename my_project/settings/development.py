"""
Development Settings for HireMind ATS.
Safe defaults for local development and testing without hardcoded passwords.
"""

import os
from .base import *

DEBUG = True

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-hiremind-dev-key-change-in-production-^9k8w7x6z5y4'
)

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,testserver'
).split(',')

# Fallback safely to SQLite if DATABASE_URL is not set
DEFAULT_DEV_DB = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
database_url = os.environ.get('DATABASE_URL', DEFAULT_DEV_DB)

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600
    )
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# In local dev, default to executing Celery tasks eagerly if Redis is not running
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'True').lower() in ('true', '1')
CELERY_TASK_EAGER_PROPAGATES = True
