from joblib import load
import numpy as np

from skimage import img_as_float
from skimage.color import rgb2gray

# from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import StandardScaler

CLASSIFIER_DUMP_PATH = 'classifier.joblib'
SCALER_DUMP_PATH = 'scaler.joblib'


# Автор: Матвей
# fixme: НЕ ЗАКОНЧЕНО \ НЕ ТЕСТИЛ \ ПРОВЕРОК НЕТ
def recognize_images(board: [np.ndarray]) -> ([[int]], [[int]]):
    """Приводит картинку к серому. Где каждый пиксель представлен интенсивностью белого.
    Загружает дамп обученной модели. И выдает предсказания для каждой клетки.
    :param board: Массив 15х15х3, где каждый пиксель представлен интенсивностями rgb.
    :return: Двумерный массив размера переданного на вход, с предсказанными клетками.
    И второй массив таких же размеров, содержащий вероятности.
    """

    images = board.reshape(225, 28, 28, 3)
    # разворачиваем массив 15x15x28x28x3 в 225x28x28x3

    for i in range(len(images)):
        images[i] = np.around(img_as_float(rgb2gray(images[i])).ravel(), decimals=2)
        # Переводим RGB в оттенки серого (из массива х3 получаем число).
        # Для этого используем формулу Y = 0.2125 R + 0.7154 G + 0.0721 B
        # Переводим в интенсивность белого в диапазон от 0 до 1.
        # Разворачиваем массив 28x28 в 784.
        # Округляем до 2-х знаков после запятой.

    # На этом этапе, у нас массив 225x784, готовый к распознаванию.

    lr_clf = load(CLASSIFIER_DUMP_PATH)  # Загружаем обученный классикатор
    scaler = load(SCALER_DUMP_PATH)  # Загружаем обученный шкалировщик
    std_images = scaler.transform(images)  # Шкалируем выборку

    # Для шкалированных данных
    std_predictions = lr_clf.predict(std_images)
    std_predictions_log_probability = lr_clf.predict_log_proba(std_images)
    std_predictions_probability = lr_clf.predict_proba(std_images)

    # Для не шкалированных данных
    predictions = lr_clf.predict(images)
    predictions_log_probability = lr_clf.predict_log_proba(images)
    predictions_probability = lr_clf.predict_proba(images)

    return list(predictions.reshape(15, 15)), list(predictions_probability.reshape(15, 15))
