

# author: Pavel
def is_hint_horizontal(hint: [[str]]) -> bool:
    """
    Проверка подсказки на горизонтальное расположение
    :param hint: матрица с символами подсказки (одно слово)
    :return: true - подсказка горизонтальная
    """

    for row in hint:
        for i in range(1, len(row)):
            if row[i] and row[i - 1]:
                return True


# author: Pavel
def get_hint_start_coord(hint: [[str]]) -> (int, int):
    """
    Получение координаты первого символа подсказки
    :param hint: матрица с символами подсказки (одно слово)
    :return: координаты первой буквы подсказки в формате y, x
    """

    # ищем первую букву, начиная с начала
    for i in range(len(hint)):
        for j in range(len(hint[i])):
            if hint[i][j]:
                return i, j
    return -1, -1


# author: Pavel
def get_hint_end_coord(hint: [[str]]) -> (int, int):
    """
    Получение координаты последнего символа подсказки
    :param hint: матрица с символами подсказки (одно слово)
    :return: координаты последней буквы подсказки в формате y, x
    """

    # ищем первую букву, начиная с конца
    for i in range(len(hint) - 1, -1, -1):
        for j in range(len(hint[i]) - 1, -1, -1):
            if hint[i][j]:
                return i, j
    return -1, -1


# author: Pavel
def get_board_with_hints(board: [[str]], hints: [[str]]) -> [[str]]:
    """
    Объединение доски с непересекающимися подсказками
    :param board: доска в виде двумерного символьного массива
    :param hints: подсказки в виде двумерных символьных массивов
    :return: объединенный двумерный символьный массив
    """

    result = []
    for row in board:
        result.append(row.copy())

    for hint in hints:
        for i in range(len(hint)):
            for j in range(len(hint[0])):
                if hint[i][j]:
                    result[i][j] = hint[i][j]
    return result


# author: Pavel
def get_hint_value_coord(hint: [[str]], combined_board: [[str]]) -> (int, int):
    """
    Поиск лучшей позиции для вывода ценности подсказки
    Выбирается одна из 10 клеток по заданным приоритетам
    Если все 10 клеток заняты, возвращается позиция начала подсказки
    :param hint: подсказка в виде двумерного символьного массива
    :param combined_board: объединение доски, подсказок и их ценностей
    в общий двумерный символьный массив
    :return: координаты в формате y, x
    """

    # получаем координаты старта и конца подсказки
    ys, xs = get_hint_start_coord(hint)  # [y, x]
    ye, xe = get_hint_end_coord(hint)  # [y, x]

    # определяем, есть ли конец доски с какой-то из сторон
    # требуется для избежания ListOutOfRange
    top_block = False
    right_block = False
    bot_block = False
    left_block = False
    if ys == 0:
        top_block = True
    if xs == 0:
        left_block = True
    if ye == len(hint) - 1:
        bot_block = True
    if xe == len(hint) - 1:
        right_block = True

    # приоритеты подсказок: 0 - максимальный, 9 - минимальный
    # горизонтально
    # 3 1 # # # 6 8 #
    # 0 с л о в о 5 #
    # 4 2 # # # 7 9 #
    # вертикально
    # 3 0 4
    # 1 с 2
    # # л #
    # # о #
    # # в #
    # 6 о 7
    # 8 5 9

    # определяем наилучшую свободную позицию
    #
    # если подсказка горизонтальная
    if is_hint_horizontal(hint):
        # 0
        # если слева нет конца доски
        if not left_block:
            # если слева нет другой фишки
            if not combined_board[ys][xs - 1]:
                # возвращаем эту позицию
                return ys, xs - 1
        # 1
        if not top_block:
            if not combined_board[ys - 1][xs]:
                return ys - 1, xs
        # 2
        if not bot_block:
            if not combined_board[ys + 1][xs]:
                return ys + 1, xs
        # 3
        if not top_block and not left_block:
            if not combined_board[ys - 1][xs - 1]:
                return ys - 1, xs - 1
        # 4
        if not bot_block and not left_block:
            if not combined_board[ys + 1][xs - 1]:
                return ys + 1, xs - 1
        # 5
        if not right_block:
            if not combined_board[ye][xe + 1]:
                return ye, xe + 1
        # 6
        if not top_block:
            if not combined_board[ye - 1][xe]:
                return ye - 1, xe
        # 7
        if not bot_block:
            if not combined_board[ye + 1][xe]:
                return ye + 1, xe
        # 8
        if not top_block and not right_block:
            if not combined_board[ye - 1][xe + 1]:
                return ye - 1, xe + 1
        # 9
        if not bot_block and not right_block:
            if not combined_board[ye + 1][xe + 1]:
                return ye + 1, xe + 1
    # если подсказка вертикальная
    else:
        # 0
        # если сверху нет конца доски
        if not top_block:
            # если сверху нет другой фишки
            if not combined_board[ys - 1][xs]:
                # возвращаем эту позицию
                return ys - 1, xs
        # 1
        if not left_block:
            if not combined_board[ys][xs - 1]:
                return ys, xs - 1
        # 2
        if not right_block:
            if not combined_board[ys][xs + 1]:
                return ys, xs + 1
        # 3
        if not top_block and not left_block:
            if not combined_board[ys - 1][xs - 1]:
                return ys - 1, xs - 1
        # 4
        if not top_block and not right_block:
            if not combined_board[ys - 1][xs + 1]:
                return ys - 1, xs + 1
        # 5
        if not bot_block:
            if not combined_board[ye + 1][xe]:
                return ye + 1, xe
        # 6
        if not left_block:
            if not combined_board[ye][xe - 1]:
                return ye, xe - 1
        # 7
        if not right_block:
            if not combined_board[ye][xe + 1]:
                return ye, xe + 1
        # 8
        if not bot_block and not left_block:
            if not combined_board[ye + 1][xe - 1]:
                return ye + 1, xe - 1
        # 9
        if not bot_block and not right_block:
            if not combined_board[ye + 1][xe + 1]:
                return ye + 1, xe + 1
    return xs, ys
