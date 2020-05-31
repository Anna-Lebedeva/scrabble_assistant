import os
from shutil import rmtree
import cv2
from scan import cut_by_external_contour
from scan import cut_by_internal_contour
from scan import cut_board_on_cells
from scan import colored_to_cropped_threshold

path_to_raw = '../../!raw_images_to_cut/'
path_to_result = '../dataset_image/'

# Зачистка и создание папок
for i in range(1, 34):
    rmtree(path_to_result + str(i), ignore_errors=True)
    os.mkdir(path_to_result + str(i))

for k, f in enumerate(os.listdir(path_to_raw), 1):
    img = cv2.imread(path_to_raw + f)
    external_crop = cut_by_external_contour(img)
    internal_crop = cut_by_internal_contour(external_crop)
    board_squares = cut_board_on_cells(internal_crop)

    row = 1
    for i in range(15):
        img = colored_to_cropped_threshold(board_squares[row - 1][i])
        cv2.imwrite(path_to_result + str(i + 1) + "/" + f, img)

    row = 2
    for i in range(15):
        img = colored_to_cropped_threshold(board_squares[row - 1][i])
        cv2.imwrite(path_to_result + str(i + 16) + "/" + f, img)

    row = 3
    for i in range(3):
        img = colored_to_cropped_threshold(board_squares[row - 1][i])
        cv2.imwrite(path_to_result + str(i + 31) + "/" + f, img)

    print(f, str(round(k/len(os.listdir(path_to_raw))*100, 1)) + "%")
