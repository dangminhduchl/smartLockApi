from django.urls import path

from .views import face_login

urlpatterns = [
    path('face_login/', face_login(), name='receive_status'),
]