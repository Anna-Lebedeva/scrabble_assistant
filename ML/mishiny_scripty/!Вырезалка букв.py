import os
import shutil
import cv2
import imutils
from scan import cut_by_external_contour
from scan import cut_by_internal_contour
from scan import cut_board_on_cells

path_to_raw = '../../!raw_images_to_cut/'
path_to_result = '../dataset_image/'

# Зачистка папок
for i in range(1, 34):
    shutil.rmtree(path_to_result + str(i), ignore_errors=True)
    os.mkdir(path_to_result + str(i))

for k, f in enumerate(os.listdir(path_to_raw), 1):
    img = imutils.resize(cut_by_external_contour(path_to_raw + f), height=750)
    img = imutils.resize(cut_by_internal_contour(img, left=3.3, top=3.0, right=0.3, bot=1.4), height=750)
    board_squares = cut_board_on_cells(img)

    stroka = 1
    for i in range(15):
        img = board_squares[stroka-1][i]
        cv2.imwrite(path_to_result + str(i + 1) + "/" + f, img)

    stroka = 2
    for i in range(15):
        img = board_squares[stroka-1][i]
        cv2.imwrite(path_to_result + str(i + 16) + "/" + f, img)

    stroka = 3
    for i in range(3):
        img = board_squares[stroka-1][i]
        cv2.imwrite(path_to_result + str(i + 31) + "/" + f, img)

    print(str(round(k/len(os.listdir(path_to_raw))*100, 1)) + "%")
