from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import SmartLockUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ChangePasswordSerializer


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

    def get(self, request):
        # if request.user.is_superuser:
        users = SmartLockUser.objects.all()
        # else:
        #     users = SmartLockUser.objects.filter(id=request.user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


from rest_framework.permissions import IsAuthenticated


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        try:
            return SmartLockUser.objects.get(pk=user_id)
        except SmartLockUser.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        user = self.get_user(int(kwargs.get('user_id')))
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        user = self.get_user(user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_user(user_id)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
        user = self.get_user(user_id)
        if user and user.id == request.user.id:
            serializer = ChangePasswordSerializer(data=request.data, context={'user': user})
            if serializer.is_valid():
                new_password = serializer.validated_data.get('new_password')
                user.set_password(new_password)
                user.save()
                return JsonResponse({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
