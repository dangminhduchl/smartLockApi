import cv2
# load image bằng OpenCV và chuyển từ BGR to RGB (dlib cần)

imagePath = "test/340964304_770498731071870_4836837574072115485_n.jpg"
unresize_image = cv2.imread(imagePath)

_image = cv2.resize(unresize_image, (300, 300))
cv2.imshow('Resized Image', unresize_image)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]


cv2.waitKey(0)

cv2.DestroyAllWindow()