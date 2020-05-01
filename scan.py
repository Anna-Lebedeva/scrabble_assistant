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
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # размытие по Гауссу, оптимальные параметры: (5, 5)
    edged = cv2.Canny(gray, 75, 150)  # изображение с границами

    # получение некого параметра для морфологического преобразования
    # оптимальные параметры: (7, 7)
    # затем само морфологическое преобразование (закрытие контуров)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    # cv2.imshow("Edged", edged)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

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

    # cv2.drawContours(image, [screen_cnt], -1, (0, 255, 0), 2)
    # cv2.imshow("Outline", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    warped = four_point_transform(orig, screen_cnt.reshape(4, 2) * ratio)  # меняем перспективу на вид сверху

    # cv2.imshow("Scanned", imutils.resize(warped, height=750))
    # cv2.waitKey(0)

    return warped


if __name__ == "__main__":
    cv2.imshow("External contour", imutils.resize(cut_by_external_contour("images/scrabble_board1.jpg"), height=750))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
