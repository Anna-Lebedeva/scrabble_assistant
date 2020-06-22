from pathlib import Path

import numpy as np
from joblib import load
from matplotlib import pyplot as plt
from skimage import img_as_ubyte
from ML.exceptions import ClfNotFoundException, ScNotFoundException

from CV.scan import IMG_SIZE, rgb_to_gray, gray_to_binary, cut_board_on_cells, crop_letter


# fixme: ПРОВЕРОК НЕТ

# Автор: Матвей
def classify_images(board: [np.ndarray],
                    clf_path: Path,
                    sc_path: Path = None,
                    probability: bool = False) -> ([[int]], [[float]]):
    """Приводит картинку к серому. Где каждый пиксель представлен интенсивностью белого.
    Загружает дамп обученной модели. И выдает предсказания для каждой клетки.

    :param board: Массив 15х15х3, где каждый пиксель представлен интенсивностями rgb.
    :param clf_path: путь к дампу с классификатором.
    :param sc_path: путь к дампу со шкалировщиком.
    :param probability: нужно ли возвращать вероятность.

    :return: Двумерный массив размера переданного на вход, с предсказанными клетками.
    И второй массив таких же размеров, содержащий вероятности.
    """

    try:  # Разворачиваем массив доски в одномерный массив
        flat_board = np.array(board).reshape(
            (board.shape[0] * board.shape[1], IMG_SIZE, IMG_SIZE))
    except ValueError:
        raise ValueError(f'Нельзя развернуть изображение формы {board.shape}')

    flat_images = np.zeros(shape=(225, IMG_SIZE * IMG_SIZE), dtype=np.uint8)

    for i in range(len(flat_board)):
        flat_images[i] = img_as_ubyte(flat_board[i]).ravel()
        # Переводим в интенсивность белого в формат ubyte.
        # Разворачиваем массив в IMG_RESOLUTION * IMG_RESOLUTION

    if not Path(clf_path).exists():
        raise ClfNotFoundException(f'Не найден дамп классификатора {clf_path}')
    clf = load(clf_path)  # Загружаем обученный классикатор

    if sc_path:
        if not Path(sc_path).exists():
            raise ScNotFoundException(f'Не найден дамп шкалировщика {sc_path}')
        scaler = load(sc_path)  # Загружаем обученный шкалировщик
        std_images = scaler.transform(flat_images)  # Шкалируем выборку

        # Для шкалированных данных
        std_predictions = clf.predict(std_images)
        # std_predictions_probability = clf.predict_proba(std_images)
        # return bla bla # fixme

    predictions = clf.predict(flat_images)
    # predictions = list(predictions)

    if probability:
        answer_proba = []
        predictions_proba = clf.predict_proba(flat_images)
        for i in predictions_proba:
            answer_proba.append(i.max())

        predictions = np.array(predictions, dtype=np.uint8).reshape(15, 15)
        for i in range(len(predictions)):
            predictions[i] = list(predictions[i])
        return list(np.array(predictions, dtype=np.uint8).reshape(15, 15)), \
               list(np.array(answer_proba).reshape(15, 15))
    # Для не шкалированных данных

    return list(predictions.reshape(15, 15))  # , \
    # list(std_predictions_probability.reshape(15, 15))


def nums_to_letters(predictions: [[int]], predict_probas: [float] = None) -> [[str]]:
    pred_letters = []
    mapping = {1: "а", 2: "б", 3: "в", 4: "г", 5: "д", 6: "е",
               7: "ж", 8: "з", 9: "и", 10: "й", 11: "к",
               12: "л", 13: "м", 14: "н", 15: "о", 16: "п",
               17: "р", 18: "с", 19: "т", 20: "у", 21: "ф",
               22: "х", 23: "ц", 24: "ч", 25: "ш", 26: "щ",
               27: "ъ", 28: "ы", 29: "ь", 30: "э",
               31: "ю", 32: "я", 33: "*", 34: "T", 35: "t",
               36: "", 37: "D", 38: "s", 39: "d"}

    # fixme временно. переписать
    for y in range(len(predictions)):
        row = []
        for x in range(len(predictions)):
            if predict_probas[y][x] < 0.5:
                row.append('')
            else:
                row.append(mapping[predictions[y][x]])
        pred_letters.append(row)

    return pred_letters


def image_to_board(img_squared: np.ndarray,
                   clf_path: Path,
                   sc_path: Path = None) -> [[str]]:
    """
    Получает обрезанную фотографию доски, применяет к ней:

    * перевод в отттенки серого с подавлением синего цвета
    * перевод в ЧБ + денойз
    * нарезку на клетки
    * коррекцию положения буквы
    * классификация буквы

    :param img_squared: обрезанную фотографию доски
    :param clf_path: путь до дампа классификатора
    :param sc_path: путь до дампа шкалировщика
    :return: массив букв распознанной позиции с фотографии
    """

    img_gray = rgb_to_gray(img_squared, [1, 0, 0])
    img_bw = gray_to_binary(img_gray)
    plt.imshow(img_bw)
    plt.show()

    board_squares = img_as_ubyte(cut_board_on_cells(img_bw))

    for i in range(len(board_squares)):
        for j in range(len(board_squares[0])):
            board_squares[i][j] = crop_letter(board_squares[i][j])  # todo check types

    predicted_letters, pred_probas = classify_images(board_squares,
                                                     clf_path=clf_path,
                                                     sc_path=sc_path,
                                                     probability=True)

    return nums_to_letters(predicted_letters, pred_probas)
