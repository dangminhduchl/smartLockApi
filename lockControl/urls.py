from django.urls import path

from .views import receive_status, ControlDevice, HistoryDevice

urlpatterns = [
    path('status/', receive_status, name='receive_status'),
    path('control/', ControlDevice.as_view(), name='control_device'),
    path('history/', HistoryDevice.as_view(), name='history')
]