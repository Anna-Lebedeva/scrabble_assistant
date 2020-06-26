#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

from joblib import dump
from skimage import img_as_bool, img_as_ubyte
from skimage.io import imread
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from preprocessing.dataset import IMG_SIZE

# from sklearn.svm import SGDClassifier

DATASET_PATH = Path('ML/dataset')
CLASSIFIER_DUMP_PATH = Path('ML/classifier.joblib')
DIMRED_DUMP_PATH = Path('ML/decomposer.joblib')
SCALER_DUMP_PATH = Path('ML/scaler.joblib')


# Автор: Матвей
def prepare_model(dataset_path: Path = DATASET_PATH,
                  clf_dump_path: Path = CLASSIFIER_DUMP_PATH,
                  dimred_dump_path: Path = None,
                  scaler_dump_path: Path = None):
    '''
    Запускаем один раз, для тренировки модели с последующим сохранением,
    для дальнейшего использования.

    :param dataset_path: путь до датасета
    :param clf_dump_path: путь до дампа классификатора
    :param dimred_dump_path: путь до дампа декомпозера
    :param scaler_dump_path: путь до дампа шкалировщика
    :return:
    '''
    letters = []
    flat_images = []

    for folder in range(1, 34):
        path_gen = Path(Path.cwd().parent / dataset_path / str(folder)).glob(
            '*.jpg')  # Создаем генератор путей картинок
        # Записываем пути картинок
        paths = [path for path in path_gen if path.is_file()]
        for i in range(len(paths)):
            flat_images.append(
                img_as_ubyte(img_as_bool(img_as_ubyte(
                    imread(paths[i])).ravel())))

            letters.append(folder)
            # Картинка представляется IMG_SIZE * IMG_SIZE признаками (пикселями),
            # в каждом из которых берем интенсивность белого
    print(
        f'Модель учится на {len(paths)} изображениях с разрешением '
        f'{IMG_SIZE}x{IMG_SIZE} в 33 категориях.')

    if dimred_dump_path:
        try:
            pca = PCA(n_components=0.9)  # Оставляем признаки, объясняющие 90% зависимостей
            flat_images = pca.fit_transform(flat_images, letters)
            print(f'Оставлено {pca.n_components_} признаков, объясняющих 90% зависимостей.')
            dump(pca, Path.cwd().parent / dimred_dump_path)

        except MemoryError:  # fixme Решить проблему с памятью
            print('Недостаточно памяти для понижения размерности. '
                  'Этап понижения размерности пропущен.')
            pass

    if scaler_dump_path:
        scaler = StandardScaler()
        flat_images = scaler.fit_transform(flat_images)
        dump(scaler, Path.cwd().parent / scaler_dump_path)

    # svm_clf = SVC(kernel='poly', degree=2, C=1, cache_size=1000)
    # svm_clf.fit(flat_images, letters)

    rf_clf = RandomForestClassifier(n_estimators=750, random_state=1, n_jobs=-1,
                                    verbose=True)
    rf_clf.fit(flat_images, letters)

    dump(rf_clf, Path.cwd().parent / clf_dump_path)
    print(f'Модель обучена. Дамп модели сохранен в {clf_dump_path}')


if __name__ == '__main__':
    prepare_model()
