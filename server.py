import os
import sys

# Set up the virtual environment path if needed for cPanel Setup Python App
# This is usually handled automatically, but good to ensure sys.path is correct
cwd = os.getcwd()
sys.path.insert(0, cwd)

from dotenv import load_dotenv
dotenv_path = os.path.join(cwd, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


os.environ['DJANGO_SETTINGS_MODULE'] = 'crm_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
