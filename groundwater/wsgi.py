"""
WSGI config for groundwater project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groundwater.settings')

application = get_wsgi_application()

# Auto-run migrations in production to ensure DB tables exist
# This is a fallback for when the start command isn't configured correctly
try:
    from django.core.management import call_command
    
    # Use a lock file to prevent race conditions with multiple workers
    lock_file = '/tmp/django_migrations_run.lock'
    
    try:
        # Try to create the lock file exclusively
        # If it exists, we assume migrations are done or in progress
        with open(lock_file, 'x') as f:
            f.write('locked')
        
        # If we got here, we are the responsible worker
        print("Attempting to apply migrations from WSGI...")
        call_command('migrate')
        # Also ensure sample data is seeded if needed, or stick to just migrations to be safe
        # call_command('seed_sample_data') 
        print("Migrations applied successfully.")
        
    except FileExistsError:
        # Migrations already handled by another worker
        pass

except Exception as e:
    print(f"Warning: Failed to run migrations in WSGI: {e}")
