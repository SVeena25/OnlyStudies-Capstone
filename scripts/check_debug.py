#!/usr/bin/env python
"""
Debug Status Checker for Development and Production Environments
"""
import os
import sys

# Temporarily rename env.py to simulate production
env_exists = os.path.exists('env.py')
if env_exists:
    os.rename('env.py', 'env.py.bak')

try:
    # Set minimal required env vars for production simulation
    os.environ['DATABASE_URL'] = 'postgresql://test'
    os.environ['SECRET_KEY'] = 'test-secret-key-for-checking'
    # Explicitly do NOT set DEBUG
    
    # Import Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'only_studies.settings')
    import django
    django.setup()
    from django.conf import settings
    
    print("\n" + "="*60)
    print("🔒 PRODUCTION ENVIRONMENT (without env.py)")
    print("="*60)
    print(f"DEBUG Status:              {settings.DEBUG}")
    print(f"SECURE_SSL_REDIRECT:       {settings.SECURE_SSL_REDIRECT}")
    print(f"SESSION_COOKIE_SECURE:     {settings.SESSION_COOKIE_SECURE}")
    print(f"CSRF_COOKIE_SECURE:        {settings.CSRF_COOKIE_SECURE}")
    if hasattr(settings, 'SECURE_HSTS_SECONDS'):
        print(f"SECURE_HSTS_SECONDS:       {settings.SECURE_HSTS_SECONDS}")
    if hasattr(settings, 'X_FRAME_OPTIONS'):
        print(f"X_FRAME_OPTIONS:           {settings.X_FRAME_OPTIONS}")
    print("="*60)
    
finally:
    # Restore env.py
    if env_exists:
        os.rename('env.py.bak', 'env.py')

# Now check development environment
print("\n" + "="*60)
print("💻 DEVELOPMENT ENVIRONMENT (with env.py)")
print("="*60)

# Reset everything
if 'django.conf' in sys.modules:
    del sys.modules['django.conf']
if 'only_studies.settings' in sys.modules:
    del sys.modules['only_studies.settings']

# Clear environment
for key in list(os.environ.keys()):
    if key in ['DATABASE_URL', 'SECRET_KEY', 'DEBUG']:
        del os.environ[key]

# Import env.py
import env

# Re-setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'only_studies.settings')
import django
django.setup()
from django.conf import settings

print(f"DEBUG Status:              {settings.DEBUG}")
print(f"SECURE_SSL_REDIRECT:       {settings.SECURE_SSL_REDIRECT}")
print(f"SESSION_COOKIE_SECURE:     {settings.SESSION_COOKIE_SECURE}")
print(f"CSRF_COOKIE_SECURE:        {settings.CSRF_COOKIE_SECURE}")
print("="*60)
print("\n✅ Configuration Check Complete!\n")
