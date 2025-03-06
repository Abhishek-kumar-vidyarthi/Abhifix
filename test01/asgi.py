"""
ASGI config for test01 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from myapp.consumers import NotificationConsumer  # Import your WebSocket consumer
from myapp.routing import websocket_urlpatterns  # Ensure this is correctly defined

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test01.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),  # Include WebSocket routing
})
