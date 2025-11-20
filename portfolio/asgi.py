"""
ASGI config for portfolio project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import logging


logger = logging.getLogger("django")
logger.info("ASGI application loaded")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

try:
    from .routing import websocket_urlpatterns
except ImportError:
    websocket_urlpatterns = []
    logger.warning("WebSocket routing not found or failed to import")


application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
    URLRouter(websocket_urlpatterns)
    
  )
})
