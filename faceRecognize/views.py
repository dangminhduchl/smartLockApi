import os

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from rest_framework import status
from rest_framework.views import APIView

from faceRecognize.service.detect_face import load_encodings, recognize_faces, find_most_frequent
from faceRecognize.service.new_user_encoding import encode_faces, encode_faces_for_id, delete_encoding_for_id
from faceRecognize.ultis import IsSuperUser
from user.models import SmartLockUser
from user.views import generate_tokens


def byte_to_json(byte_data):
    # Decode the byte object into a string
    string_data = byte_data.decode('utf-8')

    # Parse the string as JSON
    json_data = json.loads(string_data)

    return json_data


@csrf_exempt
def register(request):
    if request.method == 'POST':
        # Lấy thông tin từ request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Tạo một instance mới của User model và lưu vào cơ sở dữ liệu
        user = SmartLockUser(username=username, email=email, encode=False)
        user.set_password(password)
        user.save()
        if len(request.FILES):
            # Tạo một thư mục mới với tên là ID của user trong dataset
            user_folder = os.path.join(settings.DATASET_DIR, str(user.id))
            os.makedirs(user_folder)

            # Lưu ảnh vào thư mục vừa tạo
            for i in range(50):
                image = request.FILES.get(f'image{i + 1}')
                image_path = os.path.join(user_folder, f'image{i + 1}.jpg')
                with open(image_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)

        return JsonResponse({'message': 'Registration successful'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


@csrf_exempt
@permission_required(IsSuperUser)
def encoding_all(request):
    if request.method == 'POST':
        # Lấy thông tin từ request
        data = encode_faces(settings.DATASET_DIR, "hog", settings.ENCODING_FILE)
        if data:
            return JsonResponse({"message": f"Encoded user {data}"}, status=status.HTTP_200_OK)
        return JsonResponse({"error": "Can't encode"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EncodingView(APIView):
    permission_classes = [IsSuperUser]
    def get(self, request, user_id):
        id = encode_faces_for_id(settings.DATASET_DIR, "hog", settings.ENCODING_FILE, user_id)
        if id:
            return JsonResponse({"message": f"Encoded user {id}"}, status=status.HTTP_200_OK)

        return JsonResponse({"message": f"Can't encoded user {id}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    def delete(self, request, user_id):
        user = SmartLockUser.objects.filter(pk=user_id).first()
        deleted = delete_encoding_for_id(settings.ENCODING_FILE, user)
        if deleted:
            return JsonResponse({"message": f"Encoding for {user} deleted successfully."}, status=status.HTTP_200_OK)
        return JsonResponse({"error": f"Encoding for user {user} not found."}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def face_login(request):
    if request.method == 'POST':
        images = []
        for i in range(10):
            images.append(request.FILES.get(f'image{i + 1}'))

        encodings_dict = load_encodings(settings.ENCODING_FILE)
        if not encodings_dict:
            return JsonResponse({'error': 'Encoding file not found'}, status=status.HTTP_401_UNAUTHORIZED)

        recognized_faces = recognize_faces(images, encodings_dict)
        most_frequent_number = find_most_frequent(recognized_faces)

        if most_frequent_number != 'Unknown':
            user = User.objects.filter(id=most_frequent_number).first()
            if user:
                token = generate_tokens(user)
                return JsonResponse(token, status=status.HTTP_200_OK)

        return JsonResponse({'error': 'Cannot detect face or user not found'}, status=status.HTTP_401_UNAUTHORIZED)
