from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from faceRecognize.ultis import IsSuperUser
from .models import SmartLockUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)

    # Thêm tên người dùng vào payload của access token
    refresh['name'] = user.username
    refresh['id'] = user.id

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                tokens = generate_tokens(user)
                return Response(tokens)
            else:
                return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllUserView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        users = SmartLockUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


from rest_framework.permissions import IsAuthenticated


def can_edit_user(view_func):
    def wrapped_view(request, user_id, *args, **kwargs):
        # Kiểm tra xem người dùng có quyền IsSuperUser hoặc đang chỉnh sửa thông tin chính họ
        if request.user.is_superuser or request.user.id == int(user_id):
            return view_func(request, user_id, *args, **kwargs)
        else:
            return Response({'error': 'Unauthorized to edit this user.'}, status=status.HTTP_403_FORBIDDEN)

    return wrapped_view


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        try:
            return SmartLockUser.objects.get(pk=user_id)
        except SmartLockUser.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_user(user_id)
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @can_edit_user
    def put(self, request, user_id):
        user = self.get_user(user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @can_edit_user
    def delete(self, request, user_id):
        user = self.get_user(user_id)
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
