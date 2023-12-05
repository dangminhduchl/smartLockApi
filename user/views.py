from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import requests

from .models import SmartLockUser, NFTKey
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ChangePasswordSerializer, \
    Web3LoginSerializer, MeSerializer


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


class Web3LoginView(APIView):
    serializer_class = Web3LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            address = serializer.validated_data['address']
            user = SmartLockUser.objects.filter(username=address)
            print(user)
            if not user:
                user = SmartLockUser(username=address, encode=False)
                user.save()
            else:
                user = user[0]

            # Force nft
            response = requests.get(
                f"https://testnets-api.opensea.io/api/v2/chain/avalanche_fuji/account/{address}/nfts?collection=butterfly-791")
            if response.status_code != 200:
                return Response({'error': 'No nft'}, status=status.HTTP_401_UNAUTHORIZED)
            nft_data = response.json()
            user_nfts = user.nfts.all()
            user_nfts_dict = {nft.identifier: nft for nft in user_nfts}
            nft_created = []
            for data in nft_data.get("nfts"):
                iden = data.get("identifier")
                if iden not in user_nfts_dict:
                    metadata = requests.get(data.get("metadata_url")).json()
                    nft_created.append(
                        NFTKey(
                            identifier=iden,
                            contract=data.get("contract"),
                            image_url=metadata.get("image"),
                            user=user,
                        )
                    )
            if nft_created:
                NFTKey.objects.bulk_create(nft_created)
            tokens = generate_tokens(user)
            return Response(tokens)
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


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Force nft
        response = requests.get(
            f"https://testnets-api.opensea.io/api/v2/chain/avalanche_fuji/account/{user.username}/nfts?collection=butterfly-791")
        if response.status_code != 200:
            return Response({'error': 'No nft'}, status=status.HTTP_401_UNAUTHORIZED)
        nft_data = response.json()
        user_nfts = user.nfts.all()
        user_nfts_dict = {nft.identifier: nft for nft in user_nfts}
        nft_created = []
        for data in nft_data.get("nfts"):
            iden = data.get("identifier")
            if iden not in user_nfts_dict:
                metadata = requests.get(data.get("metadata_url")).json()
                nft_created.append(
                    NFTKey(
                        identifier=iden,
                        contract=data.get("contract"),
                        image_url=metadata.get("image"),
                        user=user,
                    )
                )
        if nft_created:
            NFTKey.objects.bulk_create(nft_created)

        serializer = MeSerializer(user)

        return Response(serializer.data)


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
