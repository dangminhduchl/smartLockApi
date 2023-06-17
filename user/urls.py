from django.urls import path

from faceRecognize.views import face_login, register
from .views import LoginView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('face_login/', face_login, name='face_login')
]