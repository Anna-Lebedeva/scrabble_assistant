import cv2
import imutils

a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for X in a:
    image = cv2.imread("images_real/TEST/" + str(X) + ".jpg")
    image = imutils.resize(image, width=1920)
    cv2.imwrite("images_real/TEST/" + str(X) + ".jpg", image)
