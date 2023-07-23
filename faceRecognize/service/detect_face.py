import pickle
from collections import Counter

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
        face_encodings = detect_face(image)  # Giả sử detect_face là hàm nhận diện khuôn mặt từ ảnh.
        names = []
        if face_encodings:
            for face_encoding in face_encodings:
                matches = compare_faces(encodings_dict["encodings"], face_encoding)  # Giả sử compare_faces là hàm so sánh encoding khuôn mặt.
                name = "Unknown"

                if True in matches:
                    matched_indices = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matched_indices:
                        name = encodings_dict["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    name = max(counts, key=counts.get)
                names.append(name)
        else:
            names.append("Unknown")  # Thêm "Unknown" vào danh sách nếu không tìm thấy khuôn mặt nào khớp.

        recognized_faces.append(names)

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


def find_most_frequent(lst):
    if not lst:
        return None

    flattened_lst = [item for sublist in lst if sublist for item in sublist]
    if not flattened_lst:
        return None

    counter = Counter(flattened_lst)
    most_frequent = counter.most_common(1)
    return most_frequent[0][0]
