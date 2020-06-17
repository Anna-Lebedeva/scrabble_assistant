from pathlib import Path

import numpy as np
from joblib import load
from skimage import img_as_float, img_as_float32

from preprocessing.model_preprocessing import IMG_RESOLUTION


# Автор: Матвей
# fixme: НЕ ДОДЕЛАНО / ПРОВЕРОК НЕТ


def classify_images(board: [np.ndarray],
                    classifier_path: Path,
                    scaler_path: Path = None) -> ([[int]], [[int]]):
    """Приводит картинку к серому. Где каждый пиксель представлен интенсивностью белого.
    Загружает дамп обученной модели. И выдает предсказания для каждой клетки.
    :param board: Массив 15х15х3, где каждый пиксель представлен интенсивностями rgb.
    :param classifier_path: путь к дампу с классификатором.
    :param scaler_path: путь к дампу со шкалировщиком.
    :return: Двумерный массив размера переданного на вход, с предсказанными клетками.
    И второй массив таких же размеров, содержащий вероятности.
    """

    images = np.array(board).reshape((225, IMG_RESOLUTION, IMG_RESOLUTION))
    # Разворачиваем массив 15x15x28x28x3 в 225x28x28x3

    flat_array = np.zeros(shape=(225, IMG_RESOLUTION * IMG_RESOLUTION))

    for i in range(len(images)):
        flat_array[i] = img_as_float32(images[i]).ravel()
        # Переводим RGB в оттенки серого (из массива х3 получаем число).
        # Переводим в интенсивность белого в диапазон от 0 до 1.
        # Разворачиваем массив в IMG_RESOLUTION * IMG_RESOLUTION

    clf = load(Path.cwd().parent / classifier_path)  # Загружаем обученный классикатор

    if scaler_path:
        scaler = load(Path.cwd().parent / scaler_path)  # Загружаем обученный шкалировщик
        std_images = scaler.transform(flat_array)  # Шкалируем выборку

        # Для шкалированных данных
        std_predictions = clf.predict(std_images)
        # std_predictions_log_probability = clf.predict_log_proba(std_images)
        # std_predictions_probability = clf.predict_proba(std_images)

    # Для не шкалированных данных
    predictions = clf.predict(flat_array)
    # predictions_log_probability = lr_clf.predict_log_proba(flat_array)
    # predictions_probability = lr_clf.predict_proba(flat_array)

    return list(predictions.reshape(15, 15))  # , \
    # list(std_predictions_probability.reshape(15, 15))


def nums_to_letters(predictions: [np.ndarray]) -> [[str]]:
    pred_letters = []
    mapping = {1: "а", 2: "б", 3: "в", 4: "г", 5: "д", 6: "е",
               7: "ж", 8: "з", 9: "и", 10: "й", 11: "к",
               12: "л", 13: "м", 14: "н", 15: "о", 16: "п",
               17: "р", 18: "с", 19: "т", 20: "у", 21: "ф",
               22: "х", 23: "ц", 24: "ч", 25: "ш", 26: "щ",
               27: "ъ", 28: "ы", 29: "ь", 30: "э",
               31: "ю", 32: "я", 33: "*", 34: "T", 35: "t",
               36: "", 37: "D", 38: "s", 39: "d"}

    # fixme временно. нужно переписать
    for y in range(len(predictions)):
        row = []
        for x in range(len(predictions)):
            row.append(mapping[predictions[y][x]])
        pred_letters.append(row)

    return pred_letters
