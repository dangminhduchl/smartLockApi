from django.urls import path
from faceRecognize.views import face_login, register, encoding_all, EncodingView
from .views import LoginView, AllUserView, UserView, Web3LoginView, Me

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login-web3/', Web3LoginView.as_view(), name='login-web3'),
    path('face_login/', face_login, name='face_login'),
    path('encodings/', encoding_all, name='encoding all'),
    path('encoding/<int:user_id>/', EncodingView.as_view(), name='encoding manage'),
    path('users/', AllUserView.as_view(), name='all user'),
    path('user/<int:user_id>/', UserView.as_view(), name='edit user'),  # Add <int:user_id> here
    path('me/', Me.as_view(), name='get current user'),  # Add <int:user_id> here
]
