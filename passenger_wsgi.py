import os
import sys

# Set up the virtual environment path if needed for cPanel Setup Python App
# This is usually handled automatically, but good to ensure sys.path is correct
cwd = os.getcwd()
sys.path.insert(0, cwd)

os.environ['DJANGO_SETTINGS_MODULE'] = 'crm_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
