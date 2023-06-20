from .consumer import StatusSocket
from django.urls import re_path


urlpatterns = [
    re_path("ws/status", StatusSocket.as_asgi())
]
