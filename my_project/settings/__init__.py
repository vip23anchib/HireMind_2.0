"""
Settings Package Entry Point.
Dynamically loads development or production settings based on DJANGO_ENV or DEBUG environment variables.
"""

import os

env = os.environ.get('DJANGO_ENV', '').lower()
debug_env = os.environ.get('DEBUG', '').lower()

if env == 'production' or debug_env == 'false':
    from .production import *
else:
    from .development import *
