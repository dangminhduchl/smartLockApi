from django.urls import path
from faceRecognize.views import face_login, register, encoding_all, encode_faces_for_id, delete_encoding_for_user
from .views import LoginView, AllUserView, UserView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('face_login/', face_login, name='face_login'),
    path('encodings/', encoding_all, name='encoding all'),
    path('encoding/<int:user_id>/', encode_faces_for_id, name='encoding'),
    path('encoding/<int:user_id>/', delete_encoding_for_user, name='delete encoding'),

    path('users/', AllUserView.as_view(), name='all user'),
    path('user/<int:user_id>/', UserView.as_view(), name='edit user'),  # Add <int:user_id> here
]
