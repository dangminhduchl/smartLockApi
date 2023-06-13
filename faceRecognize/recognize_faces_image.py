import base64
import io
import numpy as np
from PIL import Image
import face_recognition
import cv2
import pickle

def process_images(base64_images, encoding_file):
    # Tải các encoding đã biết
    print("[INFO] Đang tải encodings...")
    data = pickle.loads(open(encoding_file, "rb").read())

    recognized_people = []

    for base64_string in base64_images.get("image"):
        # Giải mã chuỗi Base64 thành dữ liệu nhị phân
        image_data = base64.b64decode(base64_string)

        # Tạo luồng trong bộ nhớ để lưu dữ liệu hình ảnh
        image_stream = io.BytesIO(image_data)

        # Mở luồng hình ảnh bằng PIL
        image = Image.open(image_stream)

        # Chuyển đổi hình ảnh thành định dạng OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Chuyển đổi hình ảnh thành định dạng RGB để nhận dạng khuôn mặt
        rgb_image = cv_image[:, :, ::-1]

        # Thực hiện nhận dạng khuôn mặt
        print("[INFO] Đang nhận dạng khuôn mặt...")
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        names = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            # So sánh khuôn mặt với các encoding đã biết
            matches = face_recognition.compare_faces(data["encodings"], face_encoding, tolerance=0.4)
            name = "Unknown"

            if True in matches:
                matched_indices = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matched_indices:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

            names.append(name)

        recognized_people.append(names)

    return recognized_people
