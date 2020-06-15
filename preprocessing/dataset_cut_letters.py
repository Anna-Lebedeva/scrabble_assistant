from pathlib import Path
from shutil import rmtree

import cv2

from CV.scan import IMAGE_RESOLUTION
from CV.scan import cut_board_on_cells
from CV.scan import cut_by_external_contour
from CV.scan import cut_by_internal_contour
from preprocessing.model_preprocessing import to_gray, to_binary

IMAGES_TO_CUT_PATH = Path('ML') / Path('raw_images_to_cut')
DATASET_PATH = Path('ML') / Path('dataset')

if __name__ == "__main__":
    # (Пере-)создание папок-категорий
    for i in range(1, 34):
        rmtree(Path.cwd().parent / DATASET_PATH / Path(str(i)), ignore_errors=True)
        (Path.cwd().parent / DATASET_PATH / Path(str(i))).mkdir(mode=0o777)

    path_gen = (Path.cwd().parent / IMAGES_TO_CUT_PATH).glob(
        '*.jpg')  # Создаем генератор путей сырых картинок
    paths = [path for path in path_gen if path.is_file()]  # Записываем пути картинок
    print(paths)

    for i in range(len(paths)):
        image = cv2.imread(str(paths[i]))
        # фильтр?
        external_crop = cut_by_external_contour(image)
        internal_crop = cut_by_internal_contour(external_crop)
        board_squares = cut_board_on_cells(internal_crop)
        flat_board = board_squares.reshape(
            (225, IMAGE_RESOLUTION, IMAGE_RESOLUTION,
             3))  # если нет фильтра то добавляется форма 3

        for j in range(1, 34):
            cell = flat_board[j]
            #binary_cell = to_binary(to_gray(cell, [0, 0, 1]))
            binary_cell = cv2.resize(cell, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
            cv2.imwrite(
                str(Path.cwd().parent / DATASET_PATH / Path(str(j)) / Path(
                    str(i) + '.jpg')),
                binary_cell)

        # Вывод процента выполнения
        print(  # f'Обработано изображение: {paths[i]} '
            f'Выполнено {str(round(i / len(paths) * 100, 1))} %')
    print('Готово!')
