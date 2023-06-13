from django.urls import path

from faceRecognize.views import face_login
from .views import RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('face_login/', face_login, name='face_login')
]