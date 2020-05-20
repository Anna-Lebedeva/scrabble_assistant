from pyimagesearch.transform import four_point_transform
import cv2
import imutils
import numpy as np
from scipy import misc
from keras.models import model_from_json
import pickle


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


def cut_by_internal_contour(img: np.ndarray,
                            left=None, top=None,
                            right=None, bot=None) -> np.ndarray:
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

    # Значения по-умолчанию
    if left is None:
        left = 4
    if top is None:
        top = 4
    if right is None:
        right = 0
    if bot is None:
        bot = 0

    cropped = img[round(top * w / 100):round(h * (1 - bot / 100)),
              round(left * h / 100):round(w * (1 - right / 100))]

    return cropped


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


def make_prediction(square: list) -> [np.ndarray]:
    """

    :param square:
    :return:
    """

    # Отключение назойливых предупреждений
    import tensorflow as tf
    import os
    tf.get_logger().setLevel('ERROR')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

    from PIL import Image

    predictions = []
    for j in range(15):
        predictions.append([])
        for i in range(15):
            image = square[j][i]
            cv2.imwrite("./" + str(i) + ".jpg", image)
            # image = cv2.imread("./" + str(i) + ".jpg", cv2.IMREAD_GRAYSCALE)
            image = misc.imread("./" + str(i) + ".jpg")
            os.remove("./" + str(i) + ".jpg")
            image = misc.imresize(image, (64, 64))
            # image = image.reshape(64, 64, 1)
            image = np.array([image])
            image = image.astype('float32')
            # image = 255 - image
            image = image / 255.0

            prediction = loaded_model.predict(image)
            prediction = int_to_word_out[np.argmax(prediction)]
            predictions[j].append(prediction)

            print(prediction)
            cv2.imshow("", square[j][i])
            cv2.waitKey()

    return predictions


if __name__ == "__main__":
    pass
    external_cropped_board = imutils.resize(cut_by_external_contour(
        "images_real/a1.jpg"), height=750)
    internal_cropped_board = imutils.resize(cut_by_internal_contour(
        external_cropped_board, left=3.3, top=3.0, right=0.3, bot=1.4),
        height=750)
    board_squares = cut_board_on_cells(internal_cropped_board)

    # cv2.imshow("External cropped board", external_cropped_board)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # cv2.imshow("Internal cropped board", internal_cropped_board)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # cv2.imshow("Grid", draw_the_grid(internal_cropped_board))
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    print(make_prediction(board_squares))
