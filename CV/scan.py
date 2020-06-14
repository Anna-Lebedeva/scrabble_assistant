from pathlib import Path

import cv2
import numpy as np
from imutils import grab_contours
from imutils import resize
from skimage.io import imshow

from CV.transform import four_point_transform
from CV.exceptions import CutException

from ML.letter_recognition import classify_images, nums_to_letters
from preprocessing.model_preprocessing import CLASSIFIER_DUMP_PATH, \
    SCALER_DUMP_PATH, to_binary, to_gray

# from keras.models import model_from_json
# import pickle
# import tensorflow as tf
# import os
# import json

# Размер изображений для тренировки и предсказаний нейросетки
# Импортируется в train и load_data, чтобы изменять значение в одном месте
IMAGE_RESOLUTION = 28


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
    x = [round(x[i]) for i in range(16)]
    y = [round(h / 15 * i) for i in range(16)]

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

            # просто берем самый большой контур с 4 точками
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
    for i in x:
        start_point = (i, 0)
        end_point = (i, h)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)
    # Горизонтальные линии
    for j in y:
        start_point = (0, j)
        end_point = (w, j)
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
    for j in range(1, 16):
        squares.append([])
        for i in range(1, 16):
            cropped = img[y[j - 1]:y[j], x[i - 1]:x[i]]
            cropped = cv2.resize(cropped, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
            squares[j - 1].append(cropped)

    return squares


# todo: сделать вывод дмухмерного массива предсказаний
#  после достижения необходимой точности предсказаний
# taken from repo:
# https://github.com/rohanthomas/Tensorflow-image-recognition,
# embedded by Mikhail
# def make_prediction(square: list) -> [np.ndarray]:
#     """
#     :param square: Массив изображений ячеек, размерность массива 15х15
#     :return: Массив предсказаний изображений
#     (пока выводит одно предсказание для отладки)
#     """
#
#     # # Отключение назойливых предупреждений
#     tf.get_logger().setLevel('ERROR')
#     os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
#
#     # Пути до файлов модели
#     path_to_classifier = "../ML/int_to_word_out.pickle"
#     path_to_model_json = "../ML/model_face.json"
#     path_to_weights = "../ML/model_face.h5"
#
#     # Импорт json для замены чисел на буквы
#     with open(file="jsons/folders_mapping.json", mode='r',
#               encoding='utf-8') as file:
#         folder_values = json.load(file)
#
#     # Загрузка классификатора
#     classifier_f = open(path_to_classifier, "rb")
#     int_to_word_out = pickle.load(classifier_f)
#     classifier_f.close()
#
#     # Загрузка json и создание модели
#     json_file = open(path_to_model_json, 'r')
#     loaded_model_json = json_file.read()
#     json_file.close()
#     loaded_model = model_from_json(loaded_model_json)
#
#     # Загрузка весов в модель
#     loaded_model.load_weights(path_to_weights)
#
#     # Создание массива предсказаний
#     predictions = []
#     for j in range(15):
#         predictions.append([])
#
#         for k in range(15):
#             img = square[j][k]
#
#             img = colored_to_cropped_threshold(img)
#
#             img = cv2.resize(img, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
#             img = np.reshape(img, (IMAGE_RESOLUTION, IMAGE_RESOLUTION, 1))
#             img = np.array([img])
#             img = img.astype('float32')
#             img = img / 255.0
#
#             prediction_arr = loaded_model.predict(img)
#             prediction = int_to_word_out[np.argmax(prediction_arr)]
#             predictions[j].append(prediction)
#
#             # Замена числа на букву
#             prediction_letter = folder_values["{}".format(prediction)]
#
#             # Вероятность
#             print("(", np.max(prediction_arr), ")", sep="", end=" ")
#             # Предсказание. Если вероятность меньше порога - это пустая клетка
#             if np.max(prediction_arr) > 0.999:
#                 print(prediction, prediction_letter)
#             else:
#                 print("Empty... Или может быть", prediction_letter)
#
#             # Изображение для проверки (временно)
#             cv2.imshow("{} {}".format(j, k), board_squares[j][k])
#             cv2.imshow("Threshold", resize(image, height=200))
#             cv2.waitKey()
#             cv2.destroyAllWindows()
#
#
#     return predictions


# author - Sergei, Mikhail
def colored_to_cropped_threshold(img: np.ndarray) -> np.ndarray:
    """
    Делает изображение чёрно-белым по порогу и отрезает лишнее
    :param img: Изображение на вход
    :return: Пороговое обрезанное изображение
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (7, 7), 0)
    # blur = cv2.blur(gray, (3, 3))
    # edges = cv2.Canny(gray, 150, 255)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    #                                cv2.THRESH_BINARY, blockSize=31, C=5)
    # thresh = cv2.erode(thresh, np.ones((3, 3), np.uint8), iterations=1)

    # Поиск контуров
    cropped = thresh.copy()
    # contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL,
    #                                        cv2.CHAIN_APPROX_NONE)

    # Перебор контуров. Если периметр достаточно большой,
    # решаем, что это буква и обрезаем картинку по
    # её левому нижнему углу
    # for idx, contour in enumerate(contours):
    #     perimeter = cv2.arcLength(contour, True)
    #     (x, y, w, h) = cv2.boundingRect(contour)
    #     if perimeter > 215:
    #         cropped = cropped[0:y + h, x:x + y + h]
    #         break

    cropped = cv2.resize(cropped, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))

    return cropped


def adaptive_equalization(img: np.ndarray) -> np.ndarray:
    # adaptive
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # equ = clahe.apply(img)
    #
    # equ = cv2.convertScaleAbs(img, alpha=1, beta=0)
    equ = img
    # non adaptive
    # equ = cv2.equalizeHist(img)

    return equ


if __name__ == "__main__":
    pass

    image = cv2.imread('test1.jpg')
    # image = cv2.imread('../resources/app_images/test.jpg')

    # image = cv2.imread('../resources/app_images/test.jpg', 0)
    # equ = cv2.equalizeHist(image)
    #
    # # create a CLAHE object (Arguments are optional).
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # cl1 = clahe.apply(image)

    external_crop = cut_by_external_contour(image)
    internal_crop = cut_by_internal_contour(external_crop)
    board_squares = cut_board_on_cells(internal_crop)
    eq = adaptive_equalization(board_squares[0][0])

    imshow(image)
    #binary_img = to_binary(to_gray(image, [1, 0, 0]))

    # eq = adaptive_equalization(board_squares[5][3])
    cv2.imshow("", resize(eq, 100))
    # cv2.imshow("", board_squares[0][0])
    cv2.waitKey()
    cv2.destroyAllWindows()

    # for i in range(15):
    #     for img in board_squares[i]:
    #         eq = adaptive_equalization(img)
    #         board_squares[i][img] = eq
    #         cv2.imshow(img, board_squares[i][img])
    #         cv2.waitKey()
    #         cv2.destroyAllWindows()

    # # тест распознавания изображений:
    # clf_path = Path.cwd().parent / CLASSIFIER_DUMP_PATH
    # sc_path = Path.cwd().parent / SCALER_DUMP_PATH
    #
    # predicted_letters = classify_images(board_squares, clf_path, sc_path)
    # pred_board = nums_to_letters(predicted_letters)
    # for row in pred_board:
    #     print(row)
    # # print(probability)

    # for j in range(15):
    #     for i in range(15):
    #         cv2.imshow("Thresh",
    #                    resize(colored_to_cropped_threshold(board_squares[j][i]),
    #                           height=150))
    #         cv2.imshow("Cell", resize(board_squares[j][i], 150))
    #         cv2.waitKey()
    #         cv2.destroyAllWindows()

    # cv2.imshow("Cell",
    #            resize(colored_to_cropped_threshold(board_squares[0][12]),
    #                   height=150))

    # print(make_prediction(board_squares))

    # cv2.imshow("External cropped board", resize(external_crop, 800))
    # cv2.imshow("Internal cropped board", resize(internal_crop, 800))
    # cv2.imshow("Cell", board_squares[0][0])
    # cv2.imshow("Grid", resize(draw_the_grid(internal_crop), 1500))

    cv2.waitKey()
    cv2.destroyAllWindows()
