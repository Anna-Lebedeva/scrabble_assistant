import os
from shutil import rmtree
import cv2
from CV.scan import cut_by_external_contour
from CV.scan import cut_by_internal_contour
from CV.scan import cut_board_on_cells
from CV.scan import adaptive_equalization
from CV.scan import IMAGE_RESOLUTION

path_to_input = '../../!raw_images_to_cut/'
path_to_output = '../dataset_image/'
function_to_apply_to_images = adaptive_equalization

for k, f in enumerate(os.listdir(path_to_input), 1):
    img = cv2.imread(path_to_input + f)
    external_crop = cut_by_external_contour(img)
    internal_crop = cut_by_internal_contour(external_crop)
    board_squares = cut_board_on_cells(internal_crop)

    empty = [4, 6]
    green = [4, 8]
    blue = [5, 5]
    yellow = [6, 2]
    red = [8, 1]
    white = [8, 8]
    all = [empty, green, blue, yellow, red, white]
    for current in all:
        img = board_squares[current[0] - 1][current[1] - 1]
        img = cv2.resize(img, (28, 28))
        cv2.imwrite(path_to_output + "Empty/" + str(current[0] * current[1]) + "_" + f, img)

    # Вывод процента выполнения
    print(f, str(round(k / len(os.listdir(path_to_input)) * 100, 1)) + "%")
