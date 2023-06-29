from .socket_consumer import StatusConsumer
from django.urls import re_path


urlpatterns = [
    re_path("ws/status", StatusConsumer.as_asgi())
]
