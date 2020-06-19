import json
import os
import pickle

import cv2
import numpy as np
import tensorflow as tf
from imutils import grab_contours, resize
from keras.models import model_from_json
from skimage import img_as_ubyte

from CV.exceptions import CutException
from CV.transform import four_point_transform
from preprocessing.model_preprocessing import rgb_to_gray, gray_to_binary

# Размер изображений для тренировки и предсказаний нейросетки
# Импортируется в train и load_data, чтобы изменять значение в одном месте
IMG_SIZE = 32


# Авторы: Миша, Матвей
def get_coordinates(img: np.ndarray) -> ([int], [int], int, int):
    """Считает координаты для разрезов, по Х, У и высоту, ширину
    :param img: изображение
    :return: 2 массива с координатами по Х, У и высоту, ширину.
    """
    # Получение высоты и ширины изображения
    (h, w) = img.shape[:2]

    # Заполнение массивов координат X для вертикальных и
    # Y для горизонтальных линий
    x = [0, 0.96 / 15 * w + 1, 1.96 / 15 * w, 2.96 / 15 * w, 3.96 / 15 * w,
         4.96 / 15 * w, 5.96 / 15 * w, 6.98 / 15 * w, 7.98 / 15 * w, 9 / 15 * w,
         10 / 15 * w, 11.01 / 15 * w, 12.01 / 15 * w, 13.03 / 15 * w,
         14.04 / 15 * w, 14.99 / 15 * w]
    x = [round(x[m]) for m in range(16)]
    y = [round(h / 15 * n) for n in range(16)]

    return x, y, h, w


# authors - Pavel, Mikhail and Sergei
def cut_by_external_contour(img: np.ndarray) -> np.ndarray:
    """
    Обрезает внешний контур объекта на изображении
    Подходит для игральной доски
    :param img: Изображение на вход
    :return: Обрезанное изображение
    """

    try:
        ratio = img.shape[0] / 750.0
        orig = img.copy()
        img = resize(img, height=750)

        # Черно-белое изображение
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Размытие по Гауссу, оптимальные параметры: (5, 5)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Изображение с границами
        edged = cv2.Canny(gray, 75, 150)

        # Получение некого параметра для морфологического преобразования
        # Оптимальные параметры: (7, 7)
        # Затем само морфологическое преобразование (закрытие контуров)
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (7, 7))
        edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        # Массив всех контуров
        contours = cv2.findContours(edged.copy(), cv2.RETR_LIST,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = grab_contours(contours)

        # Сортировка контуров по убыванию площади
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        screen_cnt = None  # самый большой контур с 4 точками
        # идем по циклу контуров от самого большого до
        # самого маленького (они уже отсортированы)
        for c in contours:
            peri = cv2.arcLength(c, True)  # периметр контура

            # аппроксимация: если точки слишком рядом - сливаем их в одну
            # это позволяет выдержать небольшую погрешность на изображении
            # оптимальный параметр от 0.02 * периметр до 0.06 * периметр
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)

            # берем самый большой контур с 4 точками
            if len(approx) == 4:
                screen_cnt = approx
                break
                # меняем перспективу на вид сверху
        cropped = four_point_transform(orig, screen_cnt.reshape(4, 2) * ratio)

    except AttributeError:
        raise CutException

    return cropped


# author - Mikhail, Pavel
def cut_by_internal_contour(img: np.ndarray,
                            left=3.95, top=4.0,
                            right=1.5, bot=1.2) -> np.ndarray:
    """
    Обрезает изображение с разных сторон
    :param img: Изображение на вход
    :param left: Сколько процентов обрезать слева
    :param top: Сколько процентов обрезать сверху
    :param right: Сколько процентов обрезать справа
    :param bot: Сколько процентов обрезать снизу
    :return: Обрезанное изображение
    """

    try:
        (h, w) = img.shape[:2]  # получение размеров игровой доски
        # обрезка
        cropped = img[round(top * w / 100):round(h * (1 - bot / 100)),
                  round(left * h / 100):round(w * (1 - right / 100))]

        (h, w) = cropped.shape[:2]  # получение размеров игрового поля

        allowable_error = 0.03  # погрешность при проверке на квадратность
        # если cropped не квадрат (допускается погрешность)

        # границы отношения ширины к высоте в пределах заданной погрешности
        top_line = 1 * (1 + allowable_error)  # верхняя граница
        bot_line = 1 / (1 + allowable_error)  # нижняя граница
        # if not (bot_line <= w / h <= top_line):
        #     raise CutException('Not a square')

    except AttributeError:
        raise

    return cropped


# author - Mikhail
def draw_the_grid(img: np.ndarray) -> np.ndarray:
    """
    Рисует сетку, по которой можно производить разбивку на 15x15 ячеек
    :param img: Изображение на вход
    :return: Изображение с сеткой
    """

    # Получение координат, высоты и ширины изображения
    x, y, h, w = get_coordinates(img)

    # Вертикальные линии
    for n in x:
        start_point = (n, 0)
        end_point = (n, h)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)
    # Горизонтальные линии
    for n in y:
        start_point = (0, n)
        end_point = (w, n)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)

    return img


# author - Mikhail
def cut_board_on_cells(img: np.ndarray) -> [np.ndarray]:
    """
    Делит изображение на квадраты-ячейки, создавая двухмерный массив из них
    :param img: Изображение на вход
    :return: Массив ячеек длиной 15x15
    """

    # Получение координат, высоты и ширины изображения
    x, y, h, w = get_coordinates(img)

    # Заполнение массива
    squares = []
    for n in range(1, 16):
        squares.append([])  # todo: переписать на numpy
        for m in range(1, 16):
            cropped = img[y[n - 1]:y[n], x[m - 1]:x[m]]
            cropped = cv2.resize(cropped, (IMG_SIZE, IMG_SIZE))
            squares[n - 1].append(cropped)

    return np.array(squares, dtype='uint8')


# author - Sergei, Mikhail
def crop_letter(img_bin: np.ndarray) -> np.ndarray:
    """
    Вырезает из клетки букву
    :param img_bin: Пороговое изображение на вход
    :return: Пороговое обрезанное изображение
    """
    # Поиск контуров
    cropped = img_bin.copy()
    cropped = img_as_ubyte(cropped)
    # cropped = cv2.fastNlMeansDenoising(cropped)
    contours, _ = cv2.findContours(cropped, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_NONE)

    # Перебор контуров. Если периметр достаточно большой,
    # решаем, что это буква и обрезаем картинку по
    # её левому нижнему углу
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        contour_perimeter = cv2.arcLength(contour, True)
        contour_square = w * h
        # # Рисовалка контуров
        # cv2.rectangle(cropped, (x, y), (x + w, y + h), (255, 0, 0), 1)
        min_letter_square = np.square(IMG_SIZE) / 9.3
        if contour_square > min_letter_square:
            hei = int(cropped.shape[1])
            wid = int(cropped.shape[0])
            if hei == wid:
                cropped = cropped[0:y + h, x:x + y + h]
            else:
                cropped = cropped[0:y + h, x:x + y + h]
            print(hei, wid)
            cv2.imshow('1', resize(cropped, 150))
            cv2.imshow('2', resize(cv2.resize(cropped, (IMG_SIZE, IMG_SIZE)), 150))
            cv2.waitKey()
            cv2.destroyAllWindows()
            break

    cropped = cv2.resize(cropped, (IMG_SIZE, IMG_SIZE))

    return cropped


# author - Mikhail
def get_prediction(square: list) -> [np.ndarray]:
    """
    :param square: Массив изображений ячеек, размерность массива 15х15
    :return: Массив предсказаний изображений
    (пока выводит одно предсказание для отладки)
    """

    # # Отключение назойливых предупреждений
    tf.get_logger().setLevel('ERROR')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # Пути до файлов модели
    CLASSIFIER_PATH = f"../ML/tf/int_to_word_out.pickle"
    MODEL_JSON_PATH = f"../ML/tf/model_face.json"
    MODEL_WEIGHTS_PATH = f"../ML/tf/model_face.h5"

    # Импорт json для замены чисел на буквы
    with open(file="../resources/jsons/folders_mapping.json", mode='r',
              encoding='utf-8') as file:
        folder_values = json.load(file)

    # Загрузка классификатора
    classifier_f = open(CLASSIFIER_PATH, "rb")
    int_to_word_out = pickle.load(classifier_f)
    classifier_f.close()

    # Загрузка json и создание модели
    json_file = open(MODEL_JSON_PATH, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # Загрузка весов в модель
    loaded_model.load_weights(MODEL_WEIGHTS_PATH)

    # Создание массива предсказаний
    predictions = []
    for r in range(15):
        predictions.append([])
        for c in range(15):
            img = square[r][c]
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            img = np.reshape(img, (IMG_SIZE, IMG_SIZE, 1))
            img = np.array([img])
            img = img.astype('float32')
            img = img / 255.0

            prediction_arr = loaded_model.predict(img)
            prediction = int_to_word_out[np.argmax(prediction_arr)]
            predictions[r].append(prediction)

            # Замена числа на букву
            prediction_letter = folder_values["{}".format(prediction)]

            if np.max(prediction_arr) > 0.999:
                predictions[r][c] = prediction_letter
            else:
                predictions[r][c] = ' '

    return predictions


if __name__ == "__main__":
    image = img_as_ubyte(
        cv2.imread('../ML/images_to_cut/IMG_20200619_091851_3.jpg'))
    # image = img_as_ubyte(cv2.imread('../resources/app_images/test.jpg'))
    img_external_crop = cut_by_external_contour(image)
    img_internal_crop = cut_by_internal_contour(img_external_crop)

    img_bw = gray_to_binary(rgb_to_gray(img_internal_crop, [0, 0, 1]))

    # plt.imshow(img_bw)
    # plt.show()
    board_squares = img_as_ubyte(cut_board_on_cells(img_bw))

    # обрезка букв в клетках
    for i in range(len(board_squares)):
        for j in range(len(board_squares[0])):
            board_squares[i][j] = crop_letter(
                board_squares[i][j])  # todo check types

    # # предсказания
    # for row in get_prediction(board_squares):
    #     print(row)
    # cv2.imshow('', resize(img_internal_crop, 700))
    # cv2.waitKey()
    # cv2.destroyAllWindows()
