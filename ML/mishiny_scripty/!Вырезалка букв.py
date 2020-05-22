import fnmatch
import os
import shutil

import cv2
import imutils

from scan import cut_board_on_cells
from scan import cut_by_external_contour
from scan import cut_by_internal_contour

path_to_raw = "../../!raw_images_to_cut/"
path_to_train = "../dataset_image/"

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
all_types = [str1, str2, str3, asterisk, red, blue, green, white, yellow, empty]

errors = []
for a in range(len(all_types)):
    current = all_types[a]

    for bukva in range(current[0], current[1]):

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
            x = bukva - current[0] + 2
        else:
            b = bukva
            x = bukva - current[0]

        # Для создания с нуля
        shutil.rmtree(path_to_train + str(b), ignore_errors=True)
        os.mkdir(path_to_train + str(b))

        for i, file in enumerate(os.listdir(path_to_raw), 1):

            # Отлов плохих фоток, которые не получится обработать
            # Нужно отключить внешний цикл
            # errors = []
            # print(i, file)
            # try:
            #     warped = cut_by_external_contour(path_to_raw + file)
            # except AttributeError:
            #     errors.append(i)
            # print(errors)

            try:
                warped = cut_by_external_contour(path_to_raw + file)
                warped = imutils.resize(cut_by_internal_contour(warped, left=3.3, top=3.0,right=0.3, bot=1.4), height=750)
                squares_array = cut_board_on_cells(warped)
                cv2.imwrite(path_to_train + str(b) + "/" + file, squares_array[current[2]][x])
                print(str(b) + ": " + file + " (" + str(round(i * 100 / len(os.listdir(path_to_raw)), 1)) + "%)")
            except AttributeError:
                errors.append(file)


print("Плохие фото: {}", format(errors))
