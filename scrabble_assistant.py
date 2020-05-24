import numpy as np

import extra as ex

# пути к json файлам
LETTERS_VALUES_FILE_PATH = 'jsons/letters_values.json'  # ценность букв
LETTERS_AMOUNT_FILE_PATH = 'jsons/letters_amount.json'  # кол-во букв
BOARD_BONUSES_FILE_PATH = 'jsons/board_bonuses.json'  # бонусы на доске

# путь к основному словарю
DICTIONARY_FILE_PATH = 'dictionary.txt'

# словарь с ценностью букв
LETTERS_VALUES = ex.read_json_to_dict(LETTERS_VALUES_FILE_PATH)
# словарь с кол-вом букв в игре
LETTERS_AMOUNT = ex.read_json_to_dict(LETTERS_AMOUNT_FILE_PATH)
# список бонусов доски в виде матрицы
BOARD_BONUSES = ex.read_json_to_list(BOARD_BONUSES_FILE_PATH)


# author - Pavel
def get_hint(board: [[str]], letters: ex.Counter) -> ([[str]], int):
    """
    Основная функция файла
    Выдает лучшую подсказку на доске из двух вариантов:
    По горизонтали и по вертикали (транспонированная доска)
    :param board: доска в виде двумерного символьного массива
    :param letters: буквы, имеющиеся у игрока
    :return: доска с лучшим словом, ценность слова
    """

    # если доска с ошибками - вернуть пустую доску
    if not is_board_correct(board):
        return get_empty_board(len(board), len(board[0])), -1

    # если доска пустая
    if is_board_empty(board):
        # запускаем для нее отдельную функцию
        return get_hint_for_empty_board(board, letters)
    # если доска не пустая
    else:
        # ищем подсказки по горизонтали и по вертикали
        hint_1, value_1 = get_horizontal_hint(board, letters)
        hint_2, value_2 = get_horizontal_hint(transpose_board(board), letters)
        # возвращаем ту подсказку, чье слово ценнее
        if value_1 >= value_2:
            return hint_1, value_1
        else:
            return transpose_board(hint_2), value_2


# author - Pavel
# todo: с регулярками будет быстрее раз в 10
def get_horizontal_hint(board: [[str]], letters: ex.Counter) -> ([[str]], int):
    """
    Дает лучшую подсказку слова на доске по горизонтали
    :param board: доска в виде двумерного символьного массива
    :param letters: буквы, имеющиеся у игрока
    :return: доска с лучшим словом, ценность слова
    """

    # параметры лучшей подсказки
    best_word = ''  # слово
    best_hint_value = 0  # цена
    best_hint_x_index = 0  # стартовый индекс
    best_hint_y_index = 0  # стартовый индекс

    marked_board = get_marked_rows(board)
    for i in range(len(marked_board)):
        with open(DICTIONARY_FILE_PATH, 'r', encoding='utf-8') as dictionary:
            for line in dictionary:  # Читаем строки из словаря
                word = line[:-1]  # без \n

                for word_start_index in \
                        get_possible_word_positions_in_row(word,
                                                           marked_board[i]):
                    word2 = ''
                    for j in range(len(word)):
                        if marked_board[i][j + word_start_index] != word[j]:
                            word2 += word[j]

                    if ex.is_word_compilable(word2, letters):
                        # считаем его ценность
                        value = evaluate_word(word, board, i,
                                              word_start_index)
                        # если ценность выше, чем у максимального,
                        # меняем лучшее слово и все его параметры на найденое
                        if value >= best_hint_value:
                            best_word = word
                            best_hint_value = value
                            best_hint_x_index = word_start_index
                            best_hint_y_index = i

    # записываем лучшее слово в матрицу доски
    best_hint = get_empty_board(len(board), len(board[0]))
    for i in range(len(best_word)):
        best_hint[best_hint_y_index][best_hint_x_index + i] = best_word[i]

    return best_hint, best_hint_value


# author - Pavel
def get_hint_for_empty_board(board: [[str]],
                             letters: ex.Counter) -> ([[str]], int):
    """
    Дает лучшую подсказку для первого хода (пустая доска)
    :param board: доска в виде двумерного символьного массива
    :param letters: буквы, имеющиеся у игрока
    :return: доска с лучшим словом, ценность этого слова на доске
    """

    mid_index = int(len(board[0]) / 2)  # 7 for standard board

    # параметры лучшей подсказки
    best_word = ''  # слово
    best_hint_value = 0  # цена
    best_hint_start_index = mid_index  # стартовый индекс

    # открываем словарь
    with open(DICTIONARY_FILE_PATH, 'r', encoding='utf-8') as dictionary:
        for line in dictionary:  # Читаем строки из словаря
            # если слово больше 7 букв - отбрасываем
            # макс. длина 8, так как в конце есть \n
            # отбрасывать \n до проверки неразумно, тратит много времени
            if len(line) <= 8:
                word = line[:-1]  # без \n
                # если слово можно собрать - пропускаем его
                if ex.is_word_compilable(word, letters):
                    # размещаем слово по всем разрешенным позициям
                    for i in range(mid_index - len(word) + 1, mid_index + 1):
                        # считаем его ценность
                        value = evaluate_word(word, board, mid_index, i)
                        # если ценность выше, чем у максимального,
                        # меняем лучшее слово и все его параметры на найденое
                        if value >= best_hint_value:
                            best_word = word
                            best_hint_value = value
                            best_hint_start_index = i

    # записываем лучшее слово в матрицу доски
    best_hint = get_empty_board(len(board), len(board[0]))
    for i in range(len(best_word)):
        best_hint[mid_index][best_hint_start_index + i] = best_word[i]

    return best_hint, best_hint_value


# authors - Matvey and Pavel
def get_empty_board(y: int, x: int) -> [[str]]:
    """
    Генерирует пустую матрицу в y строк и x столбцов
    И заполняет ее символами пустыми строками
    :param y: кол-во строк
    :param x: кол-во столбцов
    :return: матрица y*x
    """

    return [[''] * y for _ in range(x)]


# author - Pavel
def is_board_empty(board: [[str]]) -> bool:
    """
    Проверяет, является ли доска пустой
    :param board: доска в виде двумерного символьного массива
    :return: true - доска пустая
    """

    for row in board:
        for i in range(len(row)):
            # если строка не пустая
            # то вся доска не пустая
            if row[i]:
                return False
    return True


# author - Pavel
def is_board_correct(board: [[str]]) -> bool:
    """
    Проверяет доску на корректность символов внутри
    Допустимы русские буквы, * и пустая строка
    :param board: доска в виде двумерного символьного массива
    :return: true - доска корректна
    """

    for row in board:
        for char in row:
            # если символ не пустой и не * и не русская буква
            # тогда этот символ некорректен -> вся таблица некорректна
            if char and char != '*' and \
                    not ex.is_symbol_russian_letter(char):
                return False
    return True


# authors - Matvey and Pavel
def transpose_board(board: [[str]]) -> [[str]]:
    """
    Транспонирует двумерный массив
    :param board: доска в виде двумерного символьного массива
    :return: транспонированный двумерный массив
    """

    return list(np.array(board).transpose())


# author - Pavel
def get_marked_rows(board: [[str]]) -> [[str]]:
    """
    Меняет доску, помечая заблокированные клетки знаком #
    Работает только для горизонталей (rows)
    Если у клетки есть символы сверху или снизу, то клетка заблокирована
    Постобработка:
    Между двумя # пустое пространство - все клетки между ними #
    От начала до # пустое пространство - все клетки между ними #
    От # до конца пустое пространство - все клетки между ними #
    :param board: доска в виде двумерного символьного массива
    :return: одномерный массив символов(row) с заблокированными клетками
    """

    marked_board = []  # новая доска с метками
    for index in range(len(board)):  # идем по строкам
        row = board[index].copy()  # i-тая строка доски
        for symbol_index in range(len(row)):
            up_block = False  # заблокировано ли сверху
            down_block = False  # заблокировано ли снизу

            if not row[symbol_index]:  # если в клетке пусто
                if index > 0:  # если не самая верхняя строка
                    if board[index - 1][symbol_index]:  # если сверху буква
                        up_block = True
                if index < (len(board) - 1):  # если не самая нижняя строка
                    if board[index + 1][symbol_index]:  # если снизу буква
                        down_block = True
                if up_block or down_block:
                    row[symbol_index] = '#'

        # постобработка:
        # между двумя # пустое пространство - все клетки между ними #
        # от начала до # пустое пространство - все клетки между ними #
        # от # до конца пустое пространство - все клетки между ними #

        last_sharp_index = -2  # индекс последнего символа #
        # -2: символы # не встречались
        # -1: символы # встречались, но после них шли буквы

        for row_index in range(len(row)):  # идем по строкам
            if row[row_index] == '#':
                # если уже встречали #, просто перезаписываем
                if last_sharp_index == -1:
                    last_sharp_index = row_index
                # если это первая # и до этого символов не было, то все
                # клетки до этого места помечаем #
                elif last_sharp_index == -2:
                    for j in range(row_index):
                        row[j] = '#'
                    last_sharp_index = row_index
                # если уже встречали # и до этого между текущим #
                # и прошлым не было # символов, помечаем # все клетки между ними
                else:
                    for j in range(last_sharp_index + 1, row_index):
                        row[j] = '#'
                    last_sharp_index = row_index
            # если нашли какой-то символ, но не #, сбрасываем счетчик
            elif row[row_index]:
                last_sharp_index = -1

            # если дошли до конца и между последним # и концом нет символов,
            # все клетки между ними помечаем #
            if row_index == (len(row) - 1) and last_sharp_index != -1:
                for j in range(last_sharp_index + 1, row_index + 1):
                    row[j] = '#'

        marked_board.append(row)  # добавляем строку к новой доске

    return marked_board


# author - Pavel
# todo: с регулярками будет быстрее раз в 10
def get_possible_word_positions_in_row(word: str, row: [str]) -> [int]:
    """
    Находит все возможные позиции слова в строке
    :param word: слово
    :param row: строка в виде массива символов
    :return: массив индексов начала слова в строке
    """

    # индексы всех возможных позиций слова в строке
    possible_indexes = []

    # идем по строке так, чтобы слово влезло в строку
    for i in range(len(row) - len(word) + 1):

        # флаг, показывающий, все ли буквы могут поместиться в строку
        is_word_fit = True

        # счетчик совпадений по буквам
        same_letters_counter = 0

        # идем по слову
        for j in range(len(word)):
            # если буквы не совпадают и клетка в строке не пуста
            if word[j] == row[i + j]:
                same_letters_counter += 1
            elif not row[i + j]:
                pass
            else:
                # игнорируем данную позицию, идем дальше
                is_word_fit = False
                break

        # если все буквы подошли
        # и слово прикрепилось к хотя бы одной букве
        # но слово не дублирует уже написанное
        if is_word_fit and 0 < same_letters_counter < len(word):
            # предыдущий символ
            previous_sym = None
            if i != 0:
                previous_sym = row[i - 1]

            # следующий символ
            next_sym = None
            if (i + len(word)) < len(row):
                next_sym = row[i + len(word)]

            # если и слева и справа не мешается буква - можем вставить слово
            if not ex.is_symbol_russian_letter(previous_sym) and \
                    not ex.is_symbol_russian_letter(next_sym):
                possible_indexes.append(i)

    return possible_indexes


# author - Pavel
def evaluate_word(word: str, board: [[str]],
                  line_index: int, start_index: int) -> int:
    """
    Считает ценность слова, расположенного на доске,
    с учетом бонусов на доске в любых кол-вах.
    Не учитывает бонусы, которые уже были использованы.
    Если игрок доложил 7 букв - добавляет 15 баллов.
    :param word: слово, ценность которого нужно посчитать
    :param board: доска в виде двумерного символьного массива
    :param line_index: индекс строки, в которой стоит слово
    :param start_index: индекс начала слова в строке
    :return: ценность слова, с учетом бонусов
    """

    # Считываем ценность букв как словарь
    letters_values = LETTERS_VALUES

    # Считываем бонусы на доске как матрицу
    board_bonuses = BOARD_BONUSES
    # разметка ценности полей доски:
    # 00 - обычное поле
    # x2 - *2 за букву
    # x3 - *3 за букву
    # X2 - *2 за слово
    # X3 - *3 за слово
    # ST - стартовое поле

    value = 0
    new_letters_counter = 0
    word_bonuses_2x_counter = 0  # Сколько бонусов x2 слово собрали
    word_bonuses_3x_counter = 0  # Сколько бонусов x3 слово собрали

    for i in range(len(word)):  # Идем по буквам слова
        letter = word[i]

        letter_value = letters_values[letter]  # Ценность буквы без бонусов

        bonus = board_bonuses[line_index][start_index + i]
        # Бонус на клетке, где стоит буква

        # Бонусы учитываются только в том случае,
        # если они не были использованы ранее.
        # Бонус использован, если на его месте уже есть буква.

        # Если в клетке не было буквы
        if not board[line_index][start_index + i]:
            new_letters_counter += 1
            if bonus == 'x2':
                letter_value *= 2
            elif bonus == 'x3':
                letter_value *= 3
            elif bonus == 'X2':
                word_bonuses_2x_counter += 1
            elif bonus == 'X3':
                word_bonuses_3x_counter += 1

        value += letter_value
    # Считаем все собранные бонусы за слово
    value *= 2 ** word_bonuses_2x_counter
    value *= 3 ** word_bonuses_3x_counter

    # Выложил разом 7 букв - получи 15 баллов
    if new_letters_counter == 7:
        value += 15

    return value
