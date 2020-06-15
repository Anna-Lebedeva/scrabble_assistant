from pathlib import Path
from shutil import rmtree

from skimage.io import imread, imsave
from skimage.transform import resize

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

    for i in range(len(paths)):
        image = imread(str(paths[i]))

        # image_gray = to_binary(to_gray(image, [0, 0, 1]))

        external_crop = cut_by_external_contour(image)
        internal_crop = cut_by_internal_contour(external_crop)
        board_squares = cut_board_on_cells(internal_crop)
        flat_board = board_squares.reshape(
            (board_squares.shape[0] * board_squares.shape[1], IMAGE_RESOLUTION,
             IMAGE_RESOLUTION, 3))  # если нет фильтра то добавляется форма 3

        for j in range(33):  # Идем по доске как по одномерному массиву
            cell = flat_board[j]

            # фильтр
            cell_binary = to_binary(to_gray(cell, [1, 0, 0]))

            cell_binary = resize(cell_binary, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
            imsave(str(Path.cwd().parent / DATASET_PATH / Path(str(j + 1)) / Path(
                str(i) + '.jpg')), cell_binary)

        # Вывод процента выполнения
        print(  # f'Обработано изображение: {paths[i]} '
            f'Выполнено {str(round(i / len(paths) * 100, 1))} %')
    print('Готово!')
