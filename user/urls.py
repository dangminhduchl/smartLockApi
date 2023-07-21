from django.urls import path
from faceRecognize.views import face_login, register, encoding_all, EncodingView
from .views import LoginView, AllUserView, UserView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('face_login/', face_login, name='face_login'),
    path('encodings/', encoding_all, name='encoding all'),
    path('encoding/<int:user_id>/', EncodingView.as_view(), name='encoding manage'),
    path('users/', AllUserView.as_view(), name='all user'),
    path('user/<int:user_id>/', UserView.as_view(), name='edit user'),  # Add <int:user_id> here
]
