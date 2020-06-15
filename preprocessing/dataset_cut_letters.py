import time
import warnings
from pathlib import Path
from shutil import rmtree

import numpy as np
from cv2 import cv2

from skimage.io import imread, imsave
from skimage.transform import resize

from CV.scan import IMG_RES
from CV.scan import cut_board_on_cells
from CV.scan import cut_by_external_contour
from CV.scan import cut_by_internal_contour
from CV.scan import CutException
from preprocessing.model_preprocessing import to_gray, to_binary

IMAGES_TO_CUT_PATH = '!raw_images_to_cut/1'
DATASET_PATH = 'ML/dataset'

# authors - Misha, Matvey
if __name__ == "__main__":

    # Массив одномерных координат клеток с буквами и пустых
    coordinates = np.arange(33)
    coordinates = np.append(coordinates, (50, 52, 48, 76, 105, 112))
    coordinates = np.reshape(coordinates, (len(coordinates), 1))
    # Массив категорий для классификации
    categories = np.arange(1, 34)
    categories = np.append(categories,
                           ('Empty', 'Green', 'Blue', 'Yellow', 'Red', 'White'))
    # Объединение их в массив, состоящий из [координата, категория]
    crd_ctg = []
    for i in range(len(categories)):
        crd_ctg = np.append(crd_ctg, (coordinates[i][0], categories[i]))
    crd_ctg = np.reshape(crd_ctg, (len(coordinates), 2))

    # (Пере-)создание папок-категорий будущего датасета
    for folder in Path(Path.cwd().parent / DATASET_PATH).glob('*'):
        rmtree(Path(Path.cwd().parent / DATASET_PATH / Path(folder)), True)
    time.sleep(3)
    for category in categories:
        (Path(Path.cwd().parent / DATASET_PATH / Path(category))).\
            mkdir(mode=0o777)

    # Создаем генератор путей исходных изображений
    path_gen = Path(Path.cwd().parent / IMAGES_TO_CUT_PATH).glob('*.jpg')
    # Записываем пути
    paths = [path for path in path_gen if path.is_file()]

    # Массив для отлова фоток, которые не получилось обрезать
    bad_images = []
    warnings.filterwarnings('error')

    for k, file_img in enumerate(paths, 1):
        filename = str(file_img).split('\\')[-1]
        image = imread(str(file_img))
        try:
            external_crop = cut_by_external_contour(image)
            internal_crop = cut_by_internal_contour(external_crop)
            board_squares = cut_board_on_cells(internal_crop)
            # Решейп из двухмерного в одномерный массив изображений
            flat_board = board_squares.reshape(
                (board_squares.shape[0] * board_squares.shape[1], IMG_RES,
                 IMG_RES, 3))  # если нет фильтра то добавляется форма 3

            # Обработка и запись клеток
            for c in crd_ctg:
                cell = flat_board[int(c[0])]
                # cell = to_binary(to_gray(cell, [1, 0, 0]))  # фильтр для BGR
                imsave(str(Path(Path.cwd().parent / DATASET_PATH
                                / c[1] / filename)), cell)
        except (CutException, UserWarning):
            bad_images.append(filename)
        # Вывод процента выполнения
        print(filename, '|', str(round(k / len(paths) * 100, 1)) + "%")
    # Вывод результатов операции
    print('Готово!')
    if len(bad_images) > 0:
        print('Не удалось обрезать:')
        [print(b, sep=', ') for b in bad_images]
        print('Удалить?(y/n)', end=' ')
        yes = input()
        if yes == 'y':
            for b in bad_images:
                Path(Path.cwd().parent / IMAGES_TO_CUT_PATH / b).unlink()
            print('Удаление завершено')
        else:
            exit()
