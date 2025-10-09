"""
WSGI config for chaguoil project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# Import hi imelazimishwa ili kupakia storages mapema, kabla ya Django kutafuta DEFAULT_FILE_STORAGE.
import storages 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chaguoil.settings')

application = get_wsgi_application()
