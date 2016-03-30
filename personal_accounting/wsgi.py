"""
WSGI config for personal_accounting project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from envs import get_environment_settings_module


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    get_environment_settings_module()
)

application = get_wsgi_application()
