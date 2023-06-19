from .consumer import TestSocket
from django.urls import re_path


urlpatterns = [
    re_path("ws/helloworld", TestSocket.as_asgi())
]
