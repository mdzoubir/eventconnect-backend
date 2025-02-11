import os
import sys
from pathlib import Path

# Add the project directory to the sys.path
path = str(Path(__file__).parent)
if path not in sys.path:
    sys.path.append(path)

from eventconnect.wsgi import application

# Run migrations
if os.environ.get('VERCEL_ENV') == 'production':
    import django
    django.setup()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])

app = application