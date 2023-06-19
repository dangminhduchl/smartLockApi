import schedule
import time
import cv2
import os
def read_images_and_create_dataset():
    dataset_path = 'G:/Project/smartLockApi/faceRecognize/dataset'
    image_folder_path = 'G:/Project/smartLockApi/faceRecognize/images'

    # Kiểm tra xem thư mục dataset đã tồn tại chưa, nếu chưa thì tạo mới
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # Đọc tất cả các file ảnh trong thư mục ảnh
    for filename in os.listdir(image_folder_path):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(image_folder_path, filename)
            image = cv2.imread(image_path)

            # Thực hiện quá trình encoding và tạo dataset ở đây
            # ...
            # Ví dụ: Sử dụng OpenCV để xử lý ảnh và tạo dataset

            # Lưu các thông tin cần thiết vào thư mục dataset
            dataset_file_path = os.path.join(dataset_path, filename + '.txt')
            with open(dataset_file_path, 'w') as file:
                # Ghi thông tin vào file dataset
                file.write('Thông tin dataset cho ảnh ' + filename)

            # Di chuyển ảnh đã xử lý vào thư mục dataset
            new_image_path = os.path.join(dataset_path, filename)
            os.rename(image_path, new_image_path)


def run_background_task():
    dataset_path = 'G:/Project/smartLockApi/faceRecognize/dataset'
    # Đặt lịch chạy cho hàm read_images_and_create_dataset mỗi 5 phút
    schedule.every(5).minutes.do(read_images_and_create_dataset)

    while True:
        schedule.run_pending()
        time.sleep(1)


# Chạy hàm background_task
run_background_task()
