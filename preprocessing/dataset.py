#!/usr/bin/env python
# coding: utf-8

# Запускаем один раз, для нарезки датасета.

import time
import warnings
from pathlib import Path
from shutil import rmtree

import numpy as np
from skimage import img_as_ubyte
from skimage.io import imread, imsave

from CV.exceptions import CutException
from CV.scan import crop_letter, cut_board_on_cells, \
    cut_by_external_contour, cut_by_internal_contour, \
    rgb_to_gray, gray_to_binary, IMG_SIZE

IMAGES_TO_CUT_PATH = Path('ML/images_to_cut')
DATASET_PATH = Path('ML/dataset')
IS_EMPTY_CELLS_INCLUDED = False  # True, если нужны пустые клетки в датасете

# Авторы: Михаил, Матвей
if __name__ == "__main__":

    # Массив одномерных координат клеток с буквами и пустых
    coordinates = np.arange(33)
    if IS_EMPTY_CELLS_INCLUDED:
        coordinates = np.append(coordinates, (50, 52, 48, 76, 105, 112))
    coordinates = np.reshape(coordinates, (len(coordinates), 1))

    # Массив категорий для классификации
    categories = np.arange(1, 34)
    if IS_EMPTY_CELLS_INCLUDED:
        categories = np.append(categories, ('Empty', 'Green', 'Blue',
                                            'Yellow', 'Red', 'White'))
    # Объединение их в массив, состоящий из [координата, категория]
    crd_ctg = []
    for i in range(len(categories)):
        crd_ctg = np.append(crd_ctg, (str(coordinates[i][0]),
                                      str(categories[i])))  # fixme
    crd_ctg = np.reshape(crd_ctg, (len(coordinates), 2))

    # (Пере-)создание папок-категорий будущего датасета
    if not (Path.cwd().parent / DATASET_PATH).exists():
        Path.mkdir(Path.cwd().parent / DATASET_PATH)
    else:
        print("Внимание: существующий датасет будет удалён. "
              "Введите 'y', чтобы продолжить:", end=' ')
        if input() != 'y':
            exit('Операция отменена')
    for folder in (Path.cwd().parent / DATASET_PATH).glob('*'):
        rmtree(Path.cwd().parent / DATASET_PATH / Path(folder), True)
    time.sleep(3)  # Задержка перед созданием новых папок
    for category in categories:
        (Path.cwd().parent / DATASET_PATH / Path(str(category))). \
            mkdir(mode=0o777)

    # Создаем генератор путей исходных изображений
    path_gen = (Path.cwd().parent / IMAGES_TO_CUT_PATH).glob('*.jpg')
    # Записываем пути
    paths = [path for path in path_gen if path.is_file()]

    bad_images = []  # Массив для отлова фоток, которые не получилось обрезать
    warnings.filterwarnings('error')

    for k, file_img in enumerate(paths, 1):
        filename = str(file_img).split('\\')[-1]  # fixme
        image = imread(str(file_img))
        try:
            external_crop = cut_by_external_contour(image)
            internal_crop = cut_by_internal_contour(external_crop)
            board_squares = cut_board_on_cells(internal_crop)
            # Решейп из двухмерного в одномерный массив изображений
            flat_board = board_squares.reshape(
                (board_squares.shape[0] * board_squares.shape[1], IMG_SIZE,
                 IMG_SIZE, 3))  # если нет фильтра то добавляется форма 3

            # Обработка и запись клеток
            for c in crd_ctg:
                img_cell = flat_board[int(c[0])]
                img_cell = rgb_to_gray(img_cell, [1, 0, 0])
                img_cell = gray_to_binary(img_cell)
                img_cell = img_as_ubyte(img_cell)
                # Округление можно добавить тут.
                img_cell = crop_letter(img_cell)  # не работает как надо?

                imsave(str(Path.cwd().parent / DATASET_PATH / Path(c[1]) /
                           Path(filename)), img_cell)
        except (CutException, RuntimeWarning, UserWarning):
            bad_images.append(filename)
        # Вывод процента выполнения
        print(filename, '|', str(round(k / len(paths) * 100, 1)) + "%")
    # Вывод результатов операции
    print('Готово!')
    if len(bad_images) > 0:
        print('Не удалось обрезать:')
        [print(b, sep=', ', end='.\n') for b in bad_images]
        print("Введите 'y', чтобы удалить:", end=' ')
        if input() == 'y':
            for b in bad_images:
                Path(Path.cwd().parent / IMAGES_TO_CUT_PATH / b).unlink()
            print('Удаление завершено')
