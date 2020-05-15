from pyimagesearch.transform import four_point_transform
import cv2
import imutils
import numpy


def cut_by_external_contour(path: str) -> numpy.ndarray:
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
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
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


def cut_by_internal_contour(img: numpy.ndarray,
                            left_top=None, right_bot=None) -> numpy.ndarray:
    """
    Обрезает изображение с разных сторон на определённое значение
    :param img: Изображение на вход
    :param left_top: Сколько процентов обрезать слева и сверху
    :param right_bot: Сколько процентов обрезать справа и снизу
    :return: Возврат результата
    """

    # Получение высоты и ширины изображения
    (h, w) = img.shape[:2]

    # Значения по-умолчанию
    if left_top is None:
        left_top = 4
    if right_bot is None:
        right_bot = 1

    cropped = img[round(left_top * w / 100):round(h*(1-right_bot/100)),
                  round(left_top * h / 100):round(w*(1-right_bot/100))]

    return cropped


def draw_the_grid(img: numpy.ndarray) -> numpy.ndarray:
    """
    Рисует сетку, по которой можно производить разбивку на 15x15 ячеек
    :param img: Изображение на вход
    :return: Возврат результата
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


def cut_board_on_cells(img: numpy.ndarray) -> [numpy.ndarray]:
    """
    Делит изображение на квадраты-ячейки, создавая двухмерный массив из них
    :param img: Изображение на вход
    :return: Возврат результата
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


if __name__ == "__main__":
    pass
    external_cropped_board = cut_by_external_contour("images_real/c1.jpg")
    internal_cropped_board = imutils.resize(cut_by_internal_contour(
        external_cropped_board), height=750)
    board_squares = cut_board_on_cells(internal_cropped_board)

    cv2.imshow("Internal cropped board", internal_cropped_board)
    cv2.waitKey()
    cv2.destroyAllWindows()
