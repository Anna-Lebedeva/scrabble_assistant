import os
from shutil import rmtree
import cv2
from CV.scan import cut_by_external_contour
from CV.scan import cut_by_internal_contour
from CV.scan import cut_board_on_cells
from CV.scan import IMAGE_RESOLUTION

path_to_input = '../../!raw_images_to_cut/'
path_to_output = '../2/'

# (Пере-)создание папок-категорий
for i in range(1, 34):
    rmtree(path_to_output + str(i), ignore_errors=True)
    os.mkdir(path_to_output + str(i))

for k, f in enumerate(os.listdir(path_to_input), 1):
    img = cv2.imread(path_to_input + f)
    external_crop = cut_by_external_contour(img)
    internal_crop = cut_by_internal_contour(external_crop)
    board_squares = cut_board_on_cells(internal_crop)

    row = 1
    for i in range(15):
        img = board_squares[row - 1][i]

        img = cv2.resize(img, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
        cv2.imwrite(path_to_output + str(i + 1) + "/" + f, img)

    row = 2
    for i in range(15):
        img = board_squares[row - 1][i]

        img = cv2.resize(img, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
        cv2.imwrite(path_to_output + str(i + 16) + "/" + f, img)

    row = 3
    for i in range(3):
        img = board_squares[row - 1][i]

        img = cv2.resize(img, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
        cv2.imwrite(path_to_output + str(i + 31) + "/" + f, img)

    # Вывод процента выполнения
    print(f, str(round(k / len(os.listdir(path_to_input)) * 100, 1)) + "%")
