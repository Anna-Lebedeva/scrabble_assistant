from pyimagesearch.transform import four_point_transform
import cv2
import imutils
import numpy


def cut_by_external_contour(path: str) -> numpy.ndarray:
    """
    Обрезает внешний контур объекта на изображении
    Подходит для игральной доски
    :param path: путь к изображению
    :return: обрезанное изображение
    """

    image = cv2.imread(path)
    ratio = image.shape[0] / 750.0
    orig = image.copy()
    image = imutils.resize(image, height=750)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # черно-белое изображение
    # размытие по Гауссу, оптимальные параметры: (5, 5)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 150)  # изображение с границами

    # получение некого параметра для морфологического преобразования
    # оптимальные параметры: (7, 7)
    # затем само морфологическое преобразование (закрытие контуров)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    # массив всех контуров
    contours = cv2.findContours(edged.copy(), cv2.RETR_LIST,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    # сортировка контуров по убыванию площади
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


# def cut_by_internal_contour(image) -> numpy.ndarray:
#     # получаем изображение и переводим его в HSV
#     # короче у меня появился план. Суть в том что найти
#     контуры по цветам намного легче и надежнее.
#     # Можно обрезать доску по красным X3 полям.
#     Для поиска цветов и нужно переводить в HSV.
#     image = imutils.resize(image, height=550)
#     img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#
#     # диапозон красных оттенков в HSV
#     mask1 = cv2.inRange(img_hsv, (0, 65, 100), (10, 255, 255))
#     mask2 = cv2.inRange(img_hsv, (160, 65, 100), (179, 255, 255))
#
#     # Merge the mask and crop the red regions
#     mask = cv2.bitwise_or(mask1, mask2)
#     croped = cv2.bitwise_and(image, image, mask=mask)
#
#     # Ищем контуры
#     # должно найти только красные квадратики
#     counters = cv2.findContours(mask, cv2.RETR_LIST,
#     cv2.CHAIN_APPROX_SIMPLE)[0]
#     # Нужно еще убрать все мелкие контуры
#     # Соритируем контуры по размерам
#     sort = sorted(counters, key=cv2.contourArea, reverse=True)
#
#     # print(len(counters))
#     # cv2.drawContours(image, sort[:8], -1, (0, 255, 0), 2)
#     # cv2.imshow("Outline", image)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()
#
#     # Мы находим самые левые, правые и т.д. точки в каждом контуре.
#     # Среди этих точек находим самые самые правые, левые и т.д.
#     # делаем обрезку по ним т.к. после нахождения перспективы
#     в 1 функции доска расположена как квадрат.
#     most_left = 9001
#     most_right = 0
#     most_top = 9001
#     most_bot = 0
#     for i in sort[:8]:
#         ext_left = tuple(i[i[:, :, 0].argmin()][0])
#         if ext_left[0] < most_left: most_left = ext_left[0]
#
#         ext_right = tuple(i[i[:, :, 0].argmax()][0])
#         if ext_right[0] > most_right: most_right = ext_right[0]
#
#         ext_top = tuple(i[i[:, :, 1].argmin()][0])
#         if ext_top[1] < most_top: most_top = ext_top[1]
#
#         ext_bot = tuple(i[i[:, :, 1].argmax()][0])
#         if ext_bot[1] > most_bot: most_bot = ext_bot[1]
#
#         # cv2.circle(image, ext_left, 8, (0, 0, 255), -1)
#         # cv2.circle(image, array_of_right[temp], 8, (0, 255, 0), -1)
#         # cv2.circle(image, array_of_top[temp], 8, (255, 0, 0), -1)
#         # cv2.circle(image, array_of_bot[temp], 8, (255, 255, 0), -1)
#
#         # show the output image
#         # cv2.imshow("Image", image)
#         # cv2.waitKey(0)
#     # Обрезаем изначальное фото по полученным координатам
#     warped = image[most_top:most_bot, most_left:most_right]
#     # cv2.imshow("Outline", warped)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()
#     return warped


def cut_by_internal_contour(img: numpy.ndarray, from_left: int,
                            from_top=None) -> numpy.ndarray:
    """

    :param img:
    :param from_left:
    :param from_top:
    :return:
    """

    height, width = img.shape[:2]
    # Условие необязательности указания обоих параметров кадрирования
    if from_top is None:
        from_top = from_left
    cropped = img[from_left:height - 10, from_top:width - 10]
    return cropped


def draw_the_grid(img: numpy.ndarray) -> numpy.ndarray:
    """
    :param img:
    :return:
    """

    height, width = img.shape[:2]
    # заполнение массивов координат X(Y) вертикальных(горизонтальных) линий
    x = [round(width / 15 * j) for j in range(16)]
    y = [round(height / 15 * i) for i in range(16)]
    # рисовалка
    for i in x:
        start_point = (i, 0)
        end_point = (i, height)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)
    for j in y:
        start_point = (0, j)
        end_point = (width, j)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)

    return img


def cut_board_on_cells(image: numpy.ndarray)\
        -> [numpy.ndarray]:
    """

    :param image:
    :return:
    """

    height, width = image.shape[:2]

    # заполнение массивов координат X(Y) вертикальных(горизонтальных) линий
    x = [round(width / 15 * j) for j in range(16)]
    y = [round(height / 15 * i) for i in range(16)]

    squares = []

    for j in range(1, 16):
        squares.append([])
        for i in range(1, 16):
            cropped = image[y[j - 1]:y[j], x[i - 1]:x[i]]
            squares[j - 1].append(cropped)

    return squares


if __name__ == "__main__":
    pass
    external_cropped_board = cut_by_external_contour("images_real/c1.jpg")
    internal_cropped_board = imutils.resize(cut_by_internal_contour(
        external_cropped_board, from_left=48), height=750)

    board_squares = cut_board_on_cells(internal_cropped_board)

    cv2.imshow("Internal cropped board", internal_cropped_board)
    cv2.waitKey()
    cv2.destroyAllWindows()
