

# author: Pavel
def full_postprocessing(board: [[str]]) -> [[str]]:
    """
    Полная постобработка
    """

    # board = delete_asterisks(board)
    board = delete_alone_letters(board)

    return board


# author: Pavel
def delete_alone_letters(board: [[str]]) -> [[str]]:
    """
    Удаление доски от 'шумов' - символов, вокруг которых нет других букв
    Используется после распознавания доски с картинки
    :param board: доска в виде двумерного символьного массива
    :return: обработанная копия доски
    """

    result_board = []  # копия доски
    for row in board:
        # построчное копирование
        result_board.append(row.copy())

    # проверка каждого символа в доске
    for y in range(len(board)):
        for x in range(len(board[y])):
            # проверка на конец доски со всех 4 сторон
            top_end = False
            right_end = False
            bot_end = False
            left_end = False
            if y == 0:
                top_end = True
            if y == len(board) - 1:
                bot_end = True
            if x == 0:
                left_end = True
            if x == len(board[y]) - 1:
                right_end = True
            # поиск соседних букв (сверху, справа, снизу, слева)
            top_empty = True
            right_empty = True
            bot_empty = True
            left_empty = True
            # если доска не закончилась сверху
            if not top_end:
                # если в клетке сверху есть символ
                if result_board[y - 1][x]:
                    top_empty = False
            if not right_end:
                if result_board[y][x + 1]:
                    right_empty = False
            if not bot_end:
                if result_board[y + 1][x]:
                    bot_empty = False
            if not left_end:
                if result_board[y][x - 1]:
                    left_empty = False

            # если пусто по всем четырем направлениям - удаляем символ
            if top_empty and right_empty and bot_empty and left_empty:
                result_board[y][x] = ''

    return result_board


# author: Pavel
def delete_asterisks(board: [[str]]) -> [[str]]:
    """
    Удаляет все звездочки * с доски
    :return: обработанная копия доски
    """

    result_board = []  # копия доски
    for row in board:
        # построчное копирование
        result_board.append(row.copy())

    for i in range(len(result_board)):
        for j in range(len(result_board[i])):
            if result_board[i][j] == '*':
                result_board[i][j] = ''

    return result_board
