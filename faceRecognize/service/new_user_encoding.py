import copy
import json

from imutils import paths
import pickle
import cv2
import os
import face_recognition

def encode_faces(dataset_dir, detection_method, encoding_path):

    print("[INFO] Quantifying faces...")

    # Load file encoding hiện có
    if os.path.exists(encoding_path) and os.path.getsize(encoding_path) > 0:
        with open(encoding_path, "rb") as f:
            data = pickle.load(f)
        known_encodings = data["encodings"]
        known_names = data["names"]
    else:

        known_encodings = []
        known_names = []

    # Duyệt qua các thư mục người dùng
    for user_dir in os.listdir(dataset_dir):
        user_path = os.path.join(dataset_dir, user_dir)
        if not os.path.isdir(user_path):
            continue

        # Lấy ID người dùng từ tên thư mục
        user_id = user_dir

        # Kiểm tra xem người dùng đã có trong encoding chưa
        if user_id in known_names:
            continue

        # Duyệt qua các ảnh trong thư mục người dùng mới
        image_paths = list(paths.list_images(user_path))
        for (i, image_path) in enumerate(image_paths):
            print("[INFO] Processing image {}/{}".format(i + 1, len(image_paths)))
            name = user_id

            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            boxes = face_recognition.face_locations(rgb, model=detection_method)
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(name)

    # Lưu encodings và names vào file encoding
    data = {"encodings": known_encodings, "names": known_names}
    with open(encoding_path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    return data
