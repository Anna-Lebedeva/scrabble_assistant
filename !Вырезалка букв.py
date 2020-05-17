from scan import cut_by_external_contour
from scan import cut_by_internal_contour
from scan import cut_board_on_cells
import cv2
import imutils
import numpy as np
import os, fnmatch

path = "!raw_images_to_cut/"
images = fnmatch.filter(os.listdir(path), '*.jpg')
str1 = [1, 16, 0]  # Начало, конец+1, номер строки, номер столбца
str2 = [16, 31, 1]
str3 = [31, 33, 2]
asterisk = [33, 34, 2, 2]
red = [91, 92, 7, 0]
blue = [48, 49, 3, 3]
green = [46, 47, 3, 0]
white = [98, 99, 7, 7]
yellow = [77, 78, 5, 1]
empty = [78, 79, 5]

current = empty

for bukva in range(current[0], current[1]):
    for i in range(1, len((os.listdir(path)))-1):
        warped = cut_by_external_contour(path + str(i) + ".jpg")
        warped = imutils.resize(cut_by_internal_contour(warped, 4.3, 0.3), height=750)
        squares_array = cut_board_on_cells(warped)

        if current == asterisk:
            b = "Asterisk"
            x = current[3]
        elif current == red:
            b = "Red"
            x = current[3]
        elif current == blue:
            b = "Blue"
            x = current[3]
        elif current == green:
            b = "Green"
            x = current[3]
        elif current == white:
            b = "White"
            x = current[3]
        elif current == yellow:
            b = "Yellow"
            x = current[3]
        elif current == empty:
            b = "Empty"
            x = bukva-current[0]+2
        else:
            b = bukva
            x = bukva-current[0]

        cv2.imwrite("images_train/" + str(b) + "/" + str(len(os.listdir("images_train/" + str(b) + "")) + 1) + ".jpg", squares_array[current[2]][x])
        print(str(b) + ": " + str(i) + "/" + str(len(os.listdir(path))) + " :" + str(round(i*100/len(os.listdir(path)), 1)) + "%")
    bukva += 1


# print(path + images[327])

# warped = cut_by_external_contour(path + "394.jpg")
# warped = imutils.resize(cut_by_internal_contour(warped, 3, 0), height=750)
# squares_array = cut_board_on_cells(warped)
# cv2.imshow("", warped)
# cv2.waitKey()
# cv2.destroyAllWindows()
