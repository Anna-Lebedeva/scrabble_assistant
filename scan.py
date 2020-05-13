from pyimagesearch.transform import four_point_transform
import cv2
import imutils
import numpy
import tensorflow


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
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # размытие по Гауссу, оптимальные параметры: (5, 5)
    edged = cv2.Canny(gray, 75, 150)  # изображение с границами

    # получение некого параметра для морфологического преобразования
    # оптимальные параметры: (7, 7)
    # затем само морфологическое преобразование (закрытие контуров)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # массив всех контуров
    contours = imutils.grab_contours(contours)  # ?
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]  # сортировка контуров по убыванию площади

    screen_cnt = None  # самый большой контур с 4 точками
    # идем по циклу контуров от самого большого до самого маленького (они уже отсортированы)
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
    warped = four_point_transform(orig, screen_cnt.reshape(4, 2) * ratio)  # меняем перспективу на вид сверху
    return warped


def cut_by_internal_contour(image) -> numpy.ndarray:
    # получаем изображение и переводим его в HSV
    # короче у меня появился план. Суть в том что найти контуры по цветам намного легче и надежнее.
    # Можно обрезать доску по красным X3 полям. Для поиска цветов и нужно переводить в HSV.
    image = imutils.resize(image, height=550)
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # диапозон красных оттенков в HSV
    mask1 = cv2.inRange(img_hsv, (0, 65, 100), (10, 255, 255))
    mask2 = cv2.inRange(img_hsv, (160, 65, 100), (179, 255, 255))

    # Merge the mask and crop the red regions
    mask = cv2.bitwise_or(mask1, mask2)
    croped = cv2.bitwise_and(image, image, mask=mask)

    # Ищем контуры
    # должно найти только красные квадратики
    counters = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
    # Нужно еще убрать все мелкие контуры
    # Соритируем контуры по размерам
    sort = sorted(counters, key=cv2.contourArea, reverse=True)

    # print(len(counters))
    # cv2.drawContours(image, sort[:8], -1, (0, 255, 0), 2)
    # cv2.imshow("Outline", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Мы находим самые левые, правые и т.д. точки в каждом контуре.
    # Среди этих точек находим самые самые правые, левые и т.д.
    # делаем обрезку по ним т.к. после нахождения перспективы в 1 функции доска расположена как квадрат.
    most_left = 9001
    most_right = 0
    most_top = 9001
    most_bot = 0
    for i in sort[:8]:
        ext_left = tuple(i[i[:, :, 0].argmin()][0])
        if ext_left[0] < most_left: most_left = ext_left[0]

        ext_right = tuple(i[i[:, :, 0].argmax()][0])
        if ext_right[0] > most_right: most_right = ext_right[0]

        ext_top = tuple(i[i[:, :, 1].argmin()][0])
        if ext_top[1] < most_top: most_top = ext_top[1]

        ext_bot = tuple(i[i[:, :, 1].argmax()][0])
        if ext_bot[1] > most_bot: most_bot = ext_bot[1]

        # cv2.circle(image, ext_left, 8, (0, 0, 255), -1)
        # cv2.circle(image, array_of_right[temp], 8, (0, 255, 0), -1)
        # cv2.circle(image, array_of_top[temp], 8, (255, 0, 0), -1)
        # cv2.circle(image, array_of_bot[temp], 8, (255, 255, 0), -1)

        # show the output image
        # cv2.imshow("Image", image)
        # cv2.waitKey(0)
    # Обрезаем изначальное фото по полученным координатам
    warped = image[most_top:most_bot, most_left:most_right]
    # cv2.imshow("Outline", warped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return warped


# Обрезка конкретно нашей доски на черный день
# Просто отрезает определенное пространство на изображении
def MISHINA_OBREZKA_NA_CHERNY_DEN(img, from_left, from_top=None):
    height, width = img.shape[:2]
    # Условие необязательности указания обоих параметров кадрирования
    if from_top is None: from_top = from_left
    cropped = img[from_left:height - 10, from_top:width - 10]
    return cropped


# Налепливание сетки на изображение - вдруг пригодится
def MISHINA_SETKA_NA_CHERNY_DEN(img):
    height, width = img.shape[:2]
    # заполнение массивов координат X(Y) вертикальных(горизонтальных) линий
    x_array_for_vertical = [round(width / 15 * j) for j in range(16)]
    y_array_for_horizontal = [round(height / 15 * i) for i in range(16)]
    # рисовалка
    for X in x_array_for_vertical:
        start_point = (X, 0)
        end_point = (X, height)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)
    for Y in y_array_for_horizontal:
        start_point = (0, Y)
        end_point = (width, Y)
        cv2.line(img, start_point, end_point, color=(0, 255, 0), thickness=2)
    return img


# Нарезка на массив из квадратов
def MISHINA_NAREZKA_NA_CVADRATI_NA_CHERNY_DEN(image):
    height, width = image.shape[:2]
    # заполнение массивов координат X(Y) вертикальных(горизонтальных) линий
    X_array_for_vertical = [round(width / 15 * j) for j in range(16)]
    Y_array_for_horizontal = [round(height / 15 * i) for i in range(16)]

    squares_array = []
    ## вывод одномерного массива
    # for y in range(1, 16):
    #     for x in range(1, 16):
    #         cropped = image[Y_array_for_horizontal[y - 1]:Y_array_for_horizontal[y],
    #                   X_array_for_vertical[x - 1]:X_array_for_vertical[x]]
    #         squares_array.append(cropped)

    # вывод двухмерного массива
    for y in range(1, 16):
        squares_array.append([])
        for x in range(1, 16):
            cropped = image[Y_array_for_horizontal[y - 1]:Y_array_for_horizontal[y],
                      X_array_for_vertical[x - 1]:X_array_for_vertical[x]]
            squares_array[y - 1].append(cropped)

    return squares_array


if __name__ == "__main__":
    warped = cut_by_external_contour("images_real/a6.jpg")
    warped = imutils.resize(MISHINA_OBREZKA_NA_CHERNY_DEN(warped, 100), height=750)
    squares_array = MISHINA_NAREZKA_NA_CVADRATI_NA_CHERNY_DEN(warped)

    cv2.imshow("Central square", squares_array[7][7])
    cv2.waitKey()
    cv2.destroyAllWindows()
