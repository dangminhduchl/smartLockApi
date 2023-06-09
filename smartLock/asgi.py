"""
ASGI config for smartLock project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from app_socket.urls import urlpatterns
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartLock.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": AuthMiddlewareStack(URLRouter(urlpatterns))
})
