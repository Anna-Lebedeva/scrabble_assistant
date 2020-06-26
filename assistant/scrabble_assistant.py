from collections import Counter
from pathlib import Path

import numpy as np

from assistant.read_files import read_json_to_list, read_json_to_dict

# Пути к json файлам:
#
# ценность букв
LETTERS_VALUES_FILE_PATH = Path('resources/jsons/letters_values.json')
# кол-во букв
LETTERS_AMOUNT_FILE_PATH = Path('resources/jsons/letters_amount.json')
# бонусы на доске
BOARD_BONUSES_FILE_PATH = Path('resources/jsons/board_bonuses.json')

# путь к основному словарю
DICTIONARY_FILE_PATH = Path('resources/dictionaries/nouns_5000.txt')

# словарь с ценностью букв
LETTERS_VALUES = read_json_to_dict(LETTERS_VALUES_FILE_PATH)
# словарь с кол-вом букв в игре
LETTERS_AMOUNT = read_json_to_dict(LETTERS_AMOUNT_FILE_PATH)
# список бонусов доски в виде матрицы
BOARD_BONUSES = read_json_to_list(BOARD_BONUSES_FILE_PATH)


# author: Pavel
def hints_intersect(board: [[str]], hint1: [[str]], hint2: [[str]]) -> bool:
    """
    Проверка на пересечение двух подсказок
    :param board: доска в виде двумерного символьного массива
    :param hint1: первая подсказка
    :param hint2: вторая подсказка
    """

    # если на обоих подсказках в одной и той же клетке есть буквы
    # и на доске эта буква еще не стоит
    # то подсказки пересекаются
    for y in range(len(hint1)):
        for x in range(len(hint1[0])):
            if hint1[y][x] and hint2[y][x] and not board[y][x]:
                return True
    return False


# author: Pavel
def row_hints_intersect(word1: [str], xs1: int, ys1: int,
                        word2: [str], xs2: int, ys2: int) -> bool:
    """
    Проверка на пересечение двух слов, расположенных горизонтально
    """

    # если оба слова в одной строке
    if ys1 == ys2:
        xe1 = xs1 + len(word1) - 1  # индекс конца слова 1
        xe2 = xs2 + len(word2) - 1  # индекс конца слова 2
        # если начало или конец слова 1 находится внутри слова 2
        # или то же для слова 2
        # то они пересекаются
        if xs2 <= xs1 <= xe2 or xs2 <= xe1 <= xe2 \
                or xs1 <= xs2 <= xe1 or xs1 <= xe2 <= xe1:
            return True
        else:
            return False
    # если слова в разных строках - они не пересекаются
    else:
        return False


# author: Pavel
def get_n_hints(board: [[str]], letters: Counter, n: int) -> ([[[str]]], [int]):
    """
    Поиск n лучших непересекающихся подсказок
    Среди вертикальных и горизонтальных выбирается n лучших
    :param board: доска в виде двумерного символьного массива
    :param letters: буквы, имеющиеся у игрока
    :param n: кол-во необходимых подсказок
    :return: массив досок с n лучшими непересекающимися подсказками
    """

    # для пустой доски
    if is_board_empty(board):
        result = get_hint_for_empty_board(board, letters)
        result_hints = [result[0]]
        result_values = [result[1]]
        return result_hints, result_values

    x_hints, x_values = get_n_row_hints(board, letters, n)
    y_hints, y_values = get_n_row_hints(transpose_board(board), letters, n)
    for i in range(len(y_hints)):
        y_hints[i] = transpose_board(y_hints[i])

    best_hints = []  # массив n лучших подсказок
    best_hints_values = []  # массив стоимостей n лучших подсказок

    # объединение горизонтальных и вертикальных подсказок
    # сортировка по стоимости
    xi = 0  # индекс вертикальных подсказок
    yi = 0  # индекс горизонтальных подсказок
    while xi != n or yi != n:
        # обработка случая выхода за пределы массива гориз. подсказок
        if xi != n:
            x_value = x_values[xi]
        else:
            x_value = -1

        # обработка случая выхода за пределы массива верт. подсказок
        if yi != n:
            y_value = y_values[yi]
        else:
            y_value = -1

        intersection = False  # мешает ли текущая подсказка предыдущим
        # если гориз. подсказка ценнее
        if x_value >= y_value:
            # проверка на пересечение с предыдущими подсказками
            for hint in best_hints:
                if hints_intersect(board, x_hints[xi], hint):
                    intersection = True
                    break
            # если пересечений нет - добавляем
            if not intersection:
                best_hints.append(x_hints[xi])
                best_hints_values.append(x_value)
            xi += 1
        # если верт. подсказка ценнее
        else:
            # проверка на пересечение с предыдущими подсказками
            for hint in best_hints:
                if hints_intersect(board, y_hints[yi], hint):
                    intersection = True
                    break
            # если пересечений нет - добавляем
            if not intersection:
                best_hints.append(y_hints[yi])
                best_hints_values.append(y_value)
            yi += 1

    # на выход только подсказки, ценность которых выше 0
    result_hints = []
    result_values = []
    for i in range(n):
        if best_hints_values[i] > 0:
            result_hints.append(best_hints[i])
            result_values.append(best_hints_values[i])
        else:
            break
    return result_hints, result_values


# author: Pavel
def get_n_row_hints(board: [[str]], letters: Counter, n: int) -> \
        ([[[str]]], [int]):
    """
    Поиск n лучших непересекающихся горизонтальных подсказок
    :param board: доска в виде двумерного символьного массива
    :param letters: буквы, имеющиеся у игрока
    :param n: кол-во необходимых подсказок
    :return: массив из n досок с лучшими непересекающимися подсказками
    """

    # параметры лучших подсказок
    hints_words = []  # слова
    hints_values = []  # ценность
    hints_xs = []  # стартовые X индексы
    hints_ys = []  # стартовые Y индексы

    # инициализация параметров подсказок
    for i in range(n):
        hints_words.append('')
        hints_values.append(0)
        hints_xs.append(0)
        hints_ys.append(0)

    # блокировка заблокированных клеток знаком #
    marked_board = get_marked_rows(board)

    for i in range(len(marked_board)):
        with open(DICTIONARY_FILE_PATH, 'r', encoding='utf-8') as dictionary:
            for dict_line in dictionary:  # Читаем строки из словаря
                word = dict_line[:-1]  # без \n

                # идем по возможным позициям слова в строке
                for word_start_index in \
                        get_word_positions_in_row(word, marked_board[i]):
                    # то слово, которое пытаемся собрать
                    # собирается из слова в словаре за вычетом тех букв,
                    # что уже есть на доске
                    compiling_word = ''
                    for j in range(len(word)):
                        if marked_board[i][j + word_start_index] != word[j]:
                            compiling_word += word[j]

                    if is_word_compilable(compiling_word, letters):
                        # считаем его ценность
                        value = evaluate_word(word, board, i,
                                              word_start_index)
                        # если ценность выше, чем у наименее ценного в массиве,
                        # меняем наименее ценное на найденное
                        # и затем сортируем
                        if value >= hints_values[n - 1]:
                            y_index = i
                            x_index = word_start_index
                            window = -1  # индекс вставки новой подсказки
                            # если найденная подсказка менее ценная, чем n-я
                            # и пересекает ее - игнорируем найденную.
                            # если она более ценная, чем n-я,
                            # вставляем найденную
                            # и удаляем все менее ценные, пересекающие ее
                            for ni in range(n):
                                # если слово не ценнее, чем n-е
                                if value <= hints_values[ni]:
                                    # если есть пересечение
                                    if row_hints_intersect(word,
                                                           x_index,
                                                           y_index,
                                                           hints_words[ni],
                                                           hints_xs[ni],
                                                           hints_ys[ni]):
                                        # игнорируем найденную подсказку
                                        break
                                # если слово более ценное
                                else:
                                    if window == -1:
                                        window = ni
                                    # если hint[ni] пересекается с найденной
                                    if row_hints_intersect(word,
                                                           x_index,
                                                           y_index,
                                                           hints_words[ni],
                                                           hints_xs[ni],
                                                           hints_ys[ni]):
                                        # то удаляем это слово
                                        # удаляем смещением массива на 1

                                        for j in range(ni, n - 1):
                                            jp = j + 1
                                            hints_words[j] = hints_words[jp]
                                            hints_values[j] = hints_values[jp]
                                            hints_xs[j] = hints_xs[jp]
                                            hints_ys[j] = hints_ys[jp]

                                        # обнуление последнего элемента
                                        hints_words[n - 1] = ''
                                        hints_values[n - 1] = 0
                                        hints_xs[n - 1] = 0
                                        hints_ys[n - 1] = 0

                            # если подсказка подошла, вставляем ее
                            if window != -1:
                                hints_words.insert(window, word)
                                hints_values.insert(window, value)
                                hints_xs.insert(window, x_index)
                                hints_ys.insert(window, y_index)
                            # если появился элемент n+1 - вырезаем его
                            if len(hints_words) == n + 1:
                                hints_words.pop()
                                hints_values.pop()
                                hints_xs.pop()
                                hints_ys.pop()

    # запись n лучших подсказок
    best_hints = []
    best_hints_values = []
    for i in range(n):
        hint = get_empty_board(len(board), len(board[0]))
        for j in range(len(hints_words[i])):
            hint[hints_ys[i]][hints_xs[i] + j] = hints_words[i][j]
        best_hints.append(hint)
        best_hints_values.append(hints_values[i])

    return best_hints, best_hints_values


# authors: Pavel, Matvey
def get_hint_for_empty_board(board: [[str]],
                             letters: Counter) -> ([[str]], int):
    """
    Дает лучшую подсказку для первого хода (пустая доска)
    :param board: доска в виде двумерного символьного массива
    :param letters: буквы, имеющиеся у игрока
    :return: доска с лучшим словом, ценность этого слова на доске
    """

    # todo: написал качественнее, после замера скорости заменю.

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
                if is_word_compilable(word, letters):
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


# authors: Matvey, Pavel
def get_empty_board(y: int, x: int) -> [[str]]:
    """
    Генерирует пустую матрицу в y строк и x столбцов
    И заполняет ее символами пустыми строками
    :param y: кол-во строк
    :param x: кол-во столбцов
    :return: матрица y*x
    """

    return [[''] * y for _ in range(x)]


# author: Pavel
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


# author: Pavel
def get_word_positions_in_row(word: str, row: [str]) -> [int]:
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
            if not is_symbol_russian_letter(previous_sym) and \
                    not is_symbol_russian_letter(next_sym):
                possible_indexes.append(i)

    return possible_indexes


# author: Pavel
def get_used_letters(board: [[str]]) -> Counter:
    """
    Возвращает буквы, которые присутствуют на доске
    :param board: доска в виде двумерного символьного массива
    :return: Counter из использованных на доске букв
    """

    # счетчик для подсчете букв
    letters_counter = Counter()

    # идем по строкам
    for row in board:
        # формируем новый счетчик из строки и суммируем его с текущим
        letters_counter += Counter(row)

    # если в счетчике есть пустые символы
    if not letters_counter.get('') is None:
        # удаляем запись о пустых символах
        letters_counter.pop('')

    return letters_counter


# authors: Matvey, Pavel
def transpose_board(board: [[str]]) -> [[str]]:
    """
    Транспонирует двумерный массив
    :param board: доска в виде двумерного символьного массива
    :return: транспонированная доска
    """

    return list(np.array(board).transpose())


# author: Pavel
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


# author: Pavel
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


# author: Pavel
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
            if char != '' and char != '*' and \
                    not is_symbol_russian_letter(char):
                return False
    return True


# author: Pavel
def is_board_letters_amount_right(board: [[str]]) -> bool:
    """
    Проверяет не превышает ли кол-во букв на доске их кол-во в наборе
    :param board: доска в виде двумерного символьного массива
    :return: true - доска корректна
    """
    if not is_board_correct(board):
        return False

    c = get_used_letters(board)
    for key in c.keys():
        if c[key] > LETTERS_AMOUNT[key]:
            return False
    return True


# author: Matvey
def is_word_compilable(word: str, letters: Counter) -> bool:
    """
    Проверяет возможность составить слово из переданных букв.
    :param word: слово
    :param letters: буквы, имеющиеся у игрока
    :return: можно ли составить из переданных букв переданое слово
    """

    word_letters = Counter(word)  # Счетчик букв для слова
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            # Если количество букв у игрока меньше, чем букв в слове
            return False
    return True


# author: Pavel
def is_symbol_russian_letter(symbol: str) -> bool:
    """
    Проверяет, является ли символ буквой
    Считает только кириллицу
    Считает и прописные, и заглавные буквы
    :param symbol: символ
    :return: true - это буква
    """

    if symbol is None or not symbol:
        return False
    else:
        return 1040 <= ord(symbol) <= 1071 or 1072 <= ord(symbol) <= 1131
