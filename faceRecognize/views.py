import copy
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from faceRecognize.service.detect_face import load_encodings, recognize_faces
from faceRecognize.service.new_user_encoding import encode_faces


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
        user = User(username=username, email=email, password=password)
        user.save()

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
def encoding(request):
    if request.method == 'POST':
        # Lấy thông tin từ request
        username = request.POST.get('id')
        data = encode_faces(settings.DATASET_DIR, "hog", settings.ENCODING_FILE)
        print(type(data["encodings"]), type(data["names"]))
        print(type(data))
        print(data)
        data_copy = copy.deepcopy(data)
        encodings = data_copy["encodings"]

        # Kiểm tra nếu encodings là mảng numpy
        encodings = [arr.tolist() for arr in encodings]
        data_copy["encodings"] = encodings
        json_data = json.dumps(data_copy)

        return JsonResponse(json_data, safe=False)


@csrf_exempt
def face_login(request):
    if request.method == 'POST':
        images = []
        for i in range(10):
            images.append(request.FILES.get(f'image{i + 1}'))
        encodings_dict = load_encodings(settings.ENCODING_FILE)
        recognized_faces = recognize_faces(images, encodings_dict)
        return JsonResponse({'recognized_faces': recognized_faces})

    return JsonResponse({'message': 'Invalid request method'})
