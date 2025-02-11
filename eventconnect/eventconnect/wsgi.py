"""
WSGI config for eventconnect project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventconnect.eventconnect.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventconnect.settings')
    
application = get_wsgi_application()
