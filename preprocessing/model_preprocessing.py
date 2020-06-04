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
from skimage.io import imread
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

DATASET_PATH = Path('ML') / Path('color_dataset')
CLASSIFIER_DUMP_PATH = Path('ML') / Path('classifier.joblib')
SCALER_DUMP_PATH = Path('ML') / Path('scaler.joblib')

# pca t-sne rfecv psnr


if __name__ == "__main__":
    letters_data = pd.DataFrame(columns=range(28 * 28 + 1))
    letters_data = letters_data.rename(columns={784: 'letter'})

    index = 0

    for folder in range(1, 40):
        path_gen = Path(Path.cwd().parent / DATASET_PATH / str(folder)).glob(
            '*.jpg')  # Создаем генератор путей картинок
        paths = [path for path in path_gen if path.is_file()]  # Записываем пути картинок
        for i in range(len(paths)):
            letters_data.loc[index] = *np.around(
                img_as_float(rgb2gray(imread(paths[i]))).ravel(), decimals=2), folder
            # Картинка представляется 28*28 признаками (пикселями,
            # в каждом из которых берем интенсивность белого)
            # Записываем информацию в датафрейм
            index += 1

    letters_data.letter = letters_data.letter.map(int)  # Переводим номер буквы в int
    letters_y = letters_data.pop('letter')  # Выделяем целевую переменную

    scaler = StandardScaler()
    std_letters_data = scaler.fit_transform(letters_data)

    dump(scaler, Path.cwd().parent / SCALER_DUMP_PATH)

    lr_clf = LogisticRegression(C=100, max_iter=1000, n_jobs=-1, random_state=42)
    lr_clf.fit(std_letters_data, letters_y)
    dump(lr_clf, Path.cwd().parent / CLASSIFIER_DUMP_PATH)
