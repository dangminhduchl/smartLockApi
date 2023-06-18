import pickle

import cv2
import face_recognition
import numpy as np


def load_encodings(encoding_file):
    # Đọc tệp encoding.pickle và trả về danh sách encoding khuôn mặt
    with open(encoding_file, 'rb') as f:
        encodings_dict = pickle.load(f)
    return encodings_dict


def recognize_faces(images, encodings_dict):
    # Nhận diện khuôn mặt từ danh sách ảnh và so sánh với danh sách encoding
    recognized_faces = []

    for image in images:
        face_encodings = detect_face(image)

        for face_encoding in face_encodings:
            for name, encoding in encodings_dict.items():
                matches = compare_faces(encoding, face_encoding)
                if True in matches:
                    recognized_faces.append(name)

    return recognized_faces


def detect_face(image):
    # Sử dụng cv2 để nhận diện khuôn mặt từng ảnh và trả về danh sách encoding khuôn mặt
    # Sử dụng thư viện face_recognition
    image_array = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    return face_encodings


def compare_faces(encoding_list, face_encoding):
    # So sánh encoding khuôn mặt với danh sách encoding và trả về kết quả khớp
    # Sử dụng thư viện face_recognition
    return face_recognition.compare_faces(encoding_list, face_encoding)

