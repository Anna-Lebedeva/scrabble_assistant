#!/usr/bin/env python
# coding: utf-8

# Запускаем один раз, для тренировки модели с последующим сохранением,
# для дальнейшего использования.

from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from skimage import img_as_float
from skimage.color import rgb2gray
from skimage.exposure import adjust_sigmoid
from skimage.filters import threshold_isodata
from skimage.io import imread
from skimage.restoration import denoise_nl_means
from skimage.util import dtype
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

DATASET_PATH = Path('ML') / Path('dataset')
CLASSIFIER_DUMP_PATH = Path('ML') / Path('classifier.joblib')
SCALER_DUMP_PATH = Path('ML') / Path('scaler.joblib')


# t-sne psnr ecv deno


def rgb_to_gray(rgb: np.ndarray, coefficients: [float], force_copy=False) -> np.ndarray:
    """
    Т.к фишки на нашей доске синего цвета, результат будет лучше, если мы будем использовать
    не стандартные коэффициенты для перевода в оттенки серого, а те, которые будут подавлять
    синие оттенки.

    Это создаст более сильный контраст буквы. И мы сможем эффективнее
    использовать порогование.

    :param rgb: изображение в RGB формате. ИЗОБРАЖЕНИЕ НЕ ДОЛЖНО БЫТЬ ШУМНЫМ!
    :param coefficients: коэффициенты для в перевода в оттенки серого
    :param force_copy:
    :return: изображение в оттенках серого
    """

    # Проверяем форму массива, переводим в представление с плавающей точкой.
    rgb = np.asanyarray(rgb)
    if rgb.shape[-1] != 3:
        raise ValueError("Ожидается форма массива == (..., 3)), "
                         f"получено {rgb.shape}")

    rgb = dtype.img_as_float(rgb, force_copy=force_copy)
    if len(coefficients) != 3:
        raise ValueError(f"Ожидается 3 коэффициента, получено {len(coefficients)}")
    coeffs = np.array(coefficients, dtype=rgb.dtype)

    return rgb @ coeffs


def gray_to_binary(image_gray: np.ndarray) -> np.ndarray:
    """
    Переводит изображение из оттенокв серого в черно-белое.
    :param image_gray: изображение в оттенках серого
    :return: изображение в ЧБ формате
    """
    img_adj = adjust_sigmoid(image_gray)  # Регулируем контраст (сигмовидная коррекция)

    # Находим порог для изображения и возвращаем изображение в ЧБ
    return np.array((img_adj > threshold_isodata(img_adj)), dtype=image_gray.dtype)


if __name__ == "__main__":
    letters_data = pd.DataFrame(columns=range(28 * 28 + 1))
    letters_data = letters_data.rename(columns={784: 'letter'})

    index = 0

    for folder in range(1, 40):
        path_gen = Path(Path.cwd().parent / DATASET_PATH / str(folder)).glob(
            '*.jpg')  # Создаем генератор путей картинок
        paths = [path for path in path_gen if path.is_file()]  # Записываем пути картинок
        for i in range(len(paths)):
            letters_data.loc[index] = \
                *np.around(img_as_float(imread(paths[i]))).ravel(), folder
            # Переводим в оттенки серого, убираем шумы
            # Картинка представляется 28*28 признаками (пикселями,
            # в каждом из которых берем интенсивность белого)
            index += 1

    letters_data.letter = letters_data.letter.map(int)  # Переводим номер буквы в int
    letters_y = letters_data.pop('letter')  # Выделяем целевую переменную

    scaler = StandardScaler()
    std_letters_data = scaler.fit_transform(letters_data)
    dump(scaler, Path.cwd().parent / SCALER_DUMP_PATH)

    lr_clf = LogisticRegression(penalty='l1', C=1, solver='liblinear',
                                max_iter=300, n_jobs=-1, random_state=1, verbose=True)
    lr_clf.fit(std_letters_data, letters_y)
    dump(lr_clf, Path.cwd().parent / CLASSIFIER_DUMP_PATH)
