#!/usr/bin/env python
# coding: utf-8

# Запускаем один раз, для тренировки модели с последующим сохранением,
# для дальнейшего использования.

from pathlib import Path

import numpy as np
from joblib import dump
from skimage import img_as_bool, img_as_ubyte
from skimage.exposure import adjust_sigmoid
from skimage.filters import threshold_isodata
from skimage.io import imread
from skimage.restoration import denoise_tv_bregman
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

IMG_SIZE = 64

DATASET_PATH = Path('ML/dataset')
CLASSIFIER_DUMP_PATH = Path('ML/classifier.joblib')
SCALER_DUMP_PATH = Path('ML/scaler.joblib')


def rgb_to_gray(rgb: np.ndarray, coefficients: [float], force_copy=False) -> np.ndarray:
    """
    Т.к фишки на нашей доске синего цвета, результат будет лучше, если мы будем использовать
    не стандартные коэффициенты для перевода в оттенки серого, а те, которые будут подавлять
    синие оттенки.

    Это создаст более сильный контраст буквы. И мы сможем эффективнее
    использовать порогование.

    :param rgb: изображение в RGB формате.
    :param coefficients: коэффициенты для в перевода в оттенки серого
    :param force_copy:
    :return: изображение в оттенках серого
    """

    # Проверяем форму массива, переводим в представление с плавающей точкой.
    rgb = np.asanyarray(rgb)
    if rgb.shape[-1] != 3:
        raise ValueError("Ожидается форма массива == (..., 3)), "
                         f"получено {rgb.shape}")

    rgb = img_as_ubyte(rgb, force_copy=force_copy)
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
    img_denoised = denoise_tv_bregman(image_gray, weight=33)  # денойз
    # img_denoised = denoise_nl_means(image_gray)  # денойз
    img_adj = adjust_sigmoid(img_denoised, cutoff=0.4)
    # Регулируем контраст (сигмовидная коррекция)

    # Находим порог для изображения и возвращаем изображение в ЧБ
    return img_as_ubyte(img_adj > threshold_isodata(img_adj))


if __name__ == "__main__":
    letters = [] # np.array([], dtype=np.uint8)
    flat_images = []

    for folder in range(1, 34):
        path_gen = Path(Path.cwd().parent / DATASET_PATH / str(folder)).glob(
            '*.jpg')  # Создаем генератор путей картинок
        paths = [path for path in path_gen if path.is_file()]  # Записываем пути картинок
        for i in range(len(paths)):

            flat_images.append(img_as_ubyte(img_as_bool(img_as_ubyte(imread(paths[i])).ravel())))

            letters.append(folder)
            #letters = np.append(letters, folder)
            # Картинка представляется IMG_SIZE * IMG_SIZE признаками (пикселями),
            # в каждом из которых берем интенсивность белого)
    print(f'Модель учится на {len(paths)} картинках 33 букв, размером {IMG_SIZE}x{IMG_SIZE}.')

    # flat_images = img_as_ubyte(img_as_bool(flat_images))
    # scaler = StandardScaler()
    # std_letters_data = scaler.fit_transform(letters_data)
    # dump(scaler, Path.cwd().parent / SCALER_DUMP_PATH)

    svm_clf = SVC(kernel='poly', degree=2, C=1, cache_size=1000)
    svm_clf.fit(flat_images, letters)
    dump(svm_clf, Path.cwd().parent / CLASSIFIER_DUMP_PATH)
    print(f'Модель обучена. Дамп модели сохранен в {CLASSIFIER_DUMP_PATH}')
