"""
WSGI config for scaffold project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

#from .boot import fix_path
#fix_path()

import os
import logging
from django.core.wsgi import get_wsgi_application
from djangae.wsgi import DjangaeApplication
from djangae.utils import on_production

settings = "rating.settings_live" if on_production() else "rating.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
#logging.getLogger().setLevel(logging.DEBUG)

application = DjangaeApplication(get_wsgi_application())
