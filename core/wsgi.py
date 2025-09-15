"""
WSGI config for documanager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

# carica variabili di ambiente subito, metterle qui serve per l'ambiente di produzione e test
load_dotenv('.env')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# os.environ['HTTPS'] = "on"

application = get_wsgi_application()
