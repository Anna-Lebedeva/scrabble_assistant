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