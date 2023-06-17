import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from faceRecognize.recognize_faces_image import process_images


def byte_to_json(byte_data):
    # Decode the byte object into a string
    string_data = byte_data.decode('utf-8')

    # Parse the string as JSON
    json_data = json.loads(string_data)

    return json_data

@csrf_exempt
def face_login(request):
    file_path = "faceRecognize/cnn"
    face_data = byte_to_json(request.body)

    process_images(face_data, file_path)
    return 1




@csrf_exempt
def register(request):
    if request.method == 'POST':
        # Lấy thông tin từ request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Tạo một instance mới của User model và lưu vào cơ sở dữ liệu
        user = User(username=username, email=email, password=password)
        user.save()

        # Tạo một thư mục mới với tên là ID của user trong dataset
        user_folder = os.path.join('dataset', str(user.id))
        os.makedirs(user_folder)

        # Lưu ảnh vào thư mục vừa tạo
        for i in range(50):
            image = request.FILES.get(f'image{i+1}')
            image_path = os.path.join(user_folder, f'image{i+1}.jpg')
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

        return JsonResponse({'message': 'Registration successful'})
    else:
        return JsonResponse({'message': 'Invalid request method'})