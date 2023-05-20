from django.urls import path

from .views import receive_status, control_device

urlpatterns = [
    path('status/', receive_status, name='receive_status'),
    path('control/', control_device, name='control_device'),
]