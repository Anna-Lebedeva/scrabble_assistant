from pathlib import Path

import numpy as np
from joblib import load
from skimage import img_as_ubyte, img_as_bool

from preprocessing.model_preprocessing import IMG_SIZE


# Автор: Матвей
# fixme: НЕ ДОДЕЛАНО / ПРОВЕРОК НЕТ


def classify_images(board: [np.ndarray],
                    classifier_path: Path,
                    scaler_path: Path = None,
                    probability: bool = None) -> ([[int]], [[float]]):
    """Приводит картинку к серому. Где каждый пиксель представлен интенсивностью белого.
    Загружает дамп обученной модели. И выдает предсказания для каждой клетки.
    :param board: Массив 15х15х3, где каждый пиксель представлен интенсивностями rgb.
    :param classifier_path: путь к дампу с классификатором.
    :param scaler_path: путь к дампу со шкалировщиком.
    :return: Двумерный массив размера переданного на вход, с предсказанными клетками.
    И второй массив таких же размеров, содержащий вероятности.
    :param probability: нужно ли возвращать вероятность.
    """

    images = np.array(board).reshape((225, IMG_SIZE, IMG_SIZE))
    # Разворачиваем массив 15x15xIMG_SIZExIMG_SIZEx3 в 225xIMG_SIZExIMG_SIZEx3

    flat_images = np.zeros(shape=(225, IMG_SIZE * IMG_SIZE), dtype=np.uint8)

    for i in range(len(images)):
        flat_images[i] = img_as_ubyte(images[i]).ravel()
        # Переводим RGB в оттенки серого (из массива х3 получаем число).
        # Переводим в интенсивность белого в диапазон от 0 до 1.
        # Разворачиваем массив в IMG_RESOLUTION * IMG_RESOLUTION

    flat_images = img_as_ubyte(img_as_bool(flat_images))

    clf = load(Path.cwd().parent / classifier_path)  # Загружаем обученный классикатор

    if scaler_path:
        scaler = load(Path.cwd().parent / scaler_path)  # Загружаем обученный шкалировщик
        std_images = scaler.transform(flat_images)  # Шкалируем выборку

        # Для шкалированных данных
        # std_predictions = clf.predict(std_images)
        # std_predictions_log_probability = clf.predict_log_proba(std_images)
        # std_predictions_probability = clf.predict_proba(std_images)

    predictions = clf.predict(flat_images)
    #predictions = list(predictions)

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
    # predictions_log_probability = lr_clf.predict_log_proba(flat_array)
    # predictions_probability = lr_clf.predict_proba(flat_array)

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
            if predict_probas[y][x] < 0.6:
                row.append(' ')
            else:
                row.append(mapping[predictions[y][x]])
        pred_letters.append(row)

    return pred_letters
