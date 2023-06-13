import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

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
