# author - Pavel
def is_hint_horizontal(hint: [[str]]) -> bool:
    """
    Проверка подсказки на горизонтальное расположение
    :param hint: матрица с символами подсказки (одно слово)
    """

    for row in hint:
        for i in range(1, len(row)):
            if row[i] and row[i - 1]:
                return True


# author - Pavel
def get_hint_start_coord(hint: [[str]]) -> (int, int):
    """
    Получение координаты первого символа подсказки
    :param hint: матрица с символами подсказки (одно слово)
    """

    # ищем первую букву, начиная с начала
    for i in range(len(hint)):
        for j in range(len(hint[i])):
            if hint[i][j]:
                return i, j
    return -1, -1


# author - Pavel
def get_hint_end_coord(hint: [[str]]) -> (int, int):
    """
    Получение координаты последнего символа подсказки
    :param hint: матрица с символами подсказки (одно слово)
    """

    # ищем первую букву, начиная с конца
    for i in range(len(hint) - 1, -1, -1):
        for j in range(len(hint[i]) - 1, -1, -1):
            if hint[i][j]:
                return i, j
    return -1, -1


