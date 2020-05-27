from PIL import Image

from pyimagesearch.transform import four_point_transform
import cv2
import imutils
import numpy as np
from scipy import misc
from keras.models import model_from_json
import pickle
import tensorflow as tf
import os
import json

# Размер изображений для тренировки и предсказаний нейросетки
# Импортируется в train и load_data, чтобы изменять значение в одном месте
ML = 32


# authors - Pavel, Mikhail and Sergei
def cut_by_external_contour(path: str) -> np.ndarray:
    """
    Обрезает внешний контур объекта на изображении
    Подходит для игральной доски
    :param path: Путь к изображению
    :return: Обрезанное изображение
    """

    image = cv2.imread(path)
    ratio = image.shape[0] / 750.0
    orig = image.copy()
    image = imutils.resize(image, height=750)

    # Черно-белое изображение
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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
    contours = imutils.grab_contours(contours)

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

    return cropped


# author - Mikhail
def cut_by_internal_contour(img: np.ndarray,
                            left=3.3, top=3.0,
                            right=0.3, bot=1.4) -> np.ndarray:
    """
    Обрезает изображение с разных сторон на определённое значение
    :param img: Изображение на вход
    :param left: Сколько процентов обрезать слева
    :param top: Сколько процентов обрезать сверху
    :param right: Сколько процентов обрезать справа
    :param bot: Сколько процентов обрезать снизу
    :return: Обрезанное изображение
    """

    # Получение высоты и ширины изображения
    (h, w) = img.shape[:2]

    # Обрезка
    cropped = img[round(top * w / 100):round(h * (1 - bot / 100)),
                  round(left * h / 100):round(w * (1 - right / 100))]

    return cropped


# author - Mikhail
def draw_the_grid(img: np.ndarray) -> np.ndarray:
    """
    Рисует сетку, по которой можно производить разбивку на 15x15 ячеек
    :param img: Изображение на вход
    :return: Изображение с сеткой
    """

    # Получение высоты и ширины изображения
    (h, w) = img.shape[:2]

    # Заполнение массивов координат X для вертикальных и
    # Y для горизонтальных линий
    x = [round(w / 15 * j) for j in range(16)]
    y = [round(h / 15 * i) for i in range(16)]

    # Циклы, рисующие линии сетки
    for i in x:
        start_point = (i, 0)
        end_point = (i, h)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=1)
    for j in y:
        start_point = (0, j)
        end_point = (w, j)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=1)

    return img


# author - Mikhail
def cut_board_on_cells(img: np.ndarray) -> [np.ndarray]:
    """
    Делит изображение на квадраты-ячейки, создавая двухмерный массив из них
    :param img: Изображение на вход
    :return: Массив ячеек длиной 15x15
    """

    # Получение высоты и ширины изображения
    (h, w) = img.shape[:2]

    # Заполнение массивов координат X для вертикальных и
    # Y для горизонтальных линий
    x = [round(w / 15 * j) for j in range(16)]
    y = [round(h / 15 * i) for i in range(16)]

    # Заполнение массива
    squares = []
    for j in range(1, 16):
        squares.append([])
        for i in range(1, 16):
            cropped = img[y[j - 1]:y[j], x[i - 1]:x[i]]
            squares[j - 1].append(cropped)

    return squares


# todo: сделать вывод дмухмерного массива предсказаний
#  после достижения необходимой точности предсказаний
# taken from repo:
# https://github.com/rohanthomas/Tensorflow-image-recognition,
# embedded by Mikhail
def make_prediction(square: list) -> [np.ndarray]:
    """
    :param square: Массив изображений ячеек, размерность массива 15х15
    :return: Массив предсказаний изображений
    (пока выводит одно предсказание для отладки)
    """

    # # Отключение назойливых предупреждений
    tf.get_logger().setLevel('ERROR')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # Импорт файла для замены чисел на буквы
    with open(file="jsons/folders_mapping.json", mode='r',
              encoding='utf-8') as file:
        folder_values = json.load(file)

    # Пути до файлов модели
    path_to_classifier = "./ML/int_to_word_out.pickle"
    path_to_model_json = "./ML/model_face.json"
    path_to_weights = "./ML/model_face.h5"

    classifier_f = open(path_to_classifier, "rb")
    int_to_word_out = pickle.load(classifier_f)
    classifier_f.close()
    # load json and create model
    json_file = open(path_to_model_json, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(path_to_weights)

    predictions = []
    for j in range(15):
        predictions.append([])

        for k in range(15):
            image = square[j][k]
            Image.fromarray(image.astype('uint8'))

            image = colored_to_cropped_threshold(image)

            img = misc.imresize(image, (ML, ML))
            img = np.reshape(img, (ML, ML, 1))
            img = np.array([img])
            img = img.astype('float32')
            img = img / 255.0

            prediction_arr = loaded_model.predict(img)
            prediction = int_to_word_out[np.argmax(prediction_arr)]
            predictions[j].append(prediction)

            # замена числа на букву
            prediction_letter = folder_values["{}".format(prediction)]

            # Вероятность
            print("(" + str(np.max(prediction_arr)) + ")", end=" ")
            # Предсказание
            if float(np.max(prediction_arr)) > 0.999:
                print(prediction, prediction_letter)
            else:
                print("Empty" + "... Или может быть " + str(
                    prediction_letter) + "!")

            # Изображение для проверки (временно)
            cv2.imshow("{} {}".format(j, k), board_squares[j][k])
            cv2.imshow("Threshold", imutils.resize(image, height=200))
            cv2.waitKey()
            cv2.destroyAllWindows()

    return predictions


# author - Mikhail
def cut_cell(img: np.ndarray,
             left=8.0,
             top=12.0,
             right=12.0,
             bot=12.0) -> np.ndarray:
    """
    Обрезает изображение с разных сторон на определённое значение
    :param img: Изображение на вход
    :param left: Сколько процентов обрезать слева
    :param top: Сколько процентов обрезать сверху
    :param right: Сколько процентов обрезать справа
    :param bot: Сколько процентов обрезать снизу
    :return: Обрезанное изображение
    """

    # Получение высоты и ширины изображения
    (h, w) = img.shape[:2]

    # Обрезка
    cropped = img[round(top * w / 100):round(h * (1 - bot / 100)),
              round(left * h / 100):round(w * (1 - right / 100))]

    return cropped


# author - Sergei, Mikhail
def colored_to_cropped_threshold(img: np.ndarray) -> np.ndarray:
    """
    Делает изображение чёрно-белым по порогу и отрезает лишнее
    :param img: Изображение на вход
    :return: Пороговое обрезанное изображение
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.GaussianBlur(gray, (1, 1), 0)
    # gray = cv2.blur(gray, (3, 3))
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=31, C=5)
    # img_erode = cv2.erode(thresh, np.ones((1, 1), np.uint8), iterations=1)

    # Обрезалка
    cropped = thresh.copy()
    contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    marker = 0
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        if w * h > 240:
            marker = 1
            cropped = cropped[0:y+h, x:x+y+h]
            cropped = cv2.resize(cropped, (28, 28))
            break
    if marker == 0:
        cropped = cv2.resize(cropped, (28, 28))

    output = cropped  # Вывод порогового

    return output


if __name__ == "__main__":
    pass

    external_cropped_board = imutils.resize(cut_by_external_contour(
        "images_real/f4.jpg"), height=750)
    internal_cropped_board = imutils.resize(cut_by_internal_contour(
        external_cropped_board, left=3.3, top=3.0,
        right=0.3, bot=1.4), height=750)
    board_squares = cut_board_on_cells(internal_cropped_board)

    # for j in range(3):
    #     for i in range(15):
    #         cv2.imshow("Cell", imutils.resize(
    #             colored_to_cropped_threshold(board_squares[j][i]), height=150))
    #         cv2.waitKey()
    #         cv2.destroyAllWindows()
    # cv2.imshow("Cell", imutils.resize(
    #     colored_to_cropped_threshold(board_squares[0][12]), height=150))

    print(make_prediction(board_squares))

    # cv2.imshow("External cropped board", external_cropped_board)
    # cv2.imshow("Internal cropped board", internal_cropped_board)
    # cv2.imshow("Cell", board_squares[0][0])
    # cv2.imshow("Cut", cut_cell(board_squares[0][0], left=10, right=10, top=10, bot=10))
    # cv2.imshow("Grid", draw_the_grid(internal_cropped_board))

    cv2.waitKey()
    cv2.destroyAllWindows()
