#!/usr/bin/env python
# coding: utf-8

# Запускаем один раз, для тренировки модели с последующим сохранением,
# для дальнейшего использования.

from pathlib import Path

from joblib import dump
from skimage import img_as_bool, img_as_ubyte
from skimage.io import imread
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from preprocessing.dataset import IMG_SIZE

DATASET_PATH = Path('ML/dataset')
CLASSIFIER_DUMP_PATH = Path('ML/classifier.joblib')
SCALER_DUMP_PATH = Path('ML/scaler.joblib')


if __name__ == "__main__":
    letters = []
    flat_images = []

    for folder in range(1, 34):
        path_gen = Path(Path.cwd().parent / DATASET_PATH / str(folder)).glob(
            '*.jpg')  # Создаем генератор путей картинок
        paths = [path for path in path_gen if path.is_file()]  # Записываем пути картинок
        for i in range(len(paths)):
            flat_images.append(
                img_as_ubyte(img_as_bool(img_as_ubyte(imread(paths[i])).ravel())))

            letters.append(folder)
            # letters = np.append(letters, folder)
            # Картинка представляется IMG_SIZE * IMG_SIZE признаками (пикселями),
            # в каждом из которых берем интенсивность белого)
    print(
        f'Модель учится на {len(paths)} картинках 33 букв, размером {IMG_SIZE}x{IMG_SIZE}.')

    # flat_images = img_as_ubyte(img_as_bool(flat_images))
    # scaler = StandardScaler()
    # std_flat_images = scaler.fit_transform(flat_images)
    # dump(scaler, Path.cwd().parent / SCALER_DUMP_PATH)

    # svm_clf = SVC(kernel='poly', degree=2, C=1, cache_size=1000)
    # svm_clf.fit(flat_images, letters)

    rf_clf = RandomForestClassifier(n_estimators=750, random_state=1, n_jobs=-1,
                                    verbose=True)
    rf_clf.fit(flat_images, letters)

    dump(rf_clf, Path.cwd().parent / CLASSIFIER_DUMP_PATH)
    print(f'Модель обучена. Дамп модели сохранен в {CLASSIFIER_DUMP_PATH}')
