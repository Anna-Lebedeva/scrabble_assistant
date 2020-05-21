from collections import Counter
from pathlib import Path
import numpy as np
import json
import re

# пути к json файлам
#
LETTERS_VALUES_FILENAME = "jsons/letters_values.json"  # ценность букв
LETTERS_AMOUNT_FILENAME = "jsons/letters_amount.json"  # кол-во букв
BOARD_BONUSES_FILENAME = "jsons/board_bonuses.json"  # бонусы на доске

DICTIONARY_FILENAME = "dictionaries/dictionary.txt"  # путь к основному словарю


# author - Matvey
def read_json_to_dict(json_filename: str) -> dict:
    """
    Считывает json-файл в dict
    :param json_filename: имя json-файла
    :return: считанный словарь
    """
    with open(file=Path(Path.cwd() / json_filename), mode='r',
              encoding='utf-8') as file:
        return dict(json.load(file))


# author - Pavel
def read_json_to_list(json_filename: str) -> [[str]]:
    """
    Считывает json-файл в list
    :param json_filename: имя json-файла
    :return: считанный список
    """
    with open(file=Path(Path.cwd() / json_filename), mode='r',
              encoding='utf-8') as file:
        return list(json.load(file))


# словарь с ценностью букв
LETTERS_VALUES = read_json_to_dict(LETTERS_VALUES_FILENAME)
# словарь с кол-вом букв в игре
LETTERS_AMOUNT = read_json_to_dict(LETTERS_AMOUNT_FILENAME)
# список бонусов доски в виде матрицы
BOARD_BONUSES = read_json_to_list(BOARD_BONUSES_FILENAME)


# authors - Pavel and Matvey
# todo: не завершено
def get_best_hint(board: [[str]], letters: Counter) -> [[str]]:
    """
    Дает лучшую подсказку слова на доске.
    :param board: символьный двумерный массив доски
    :param letters: набор букв игрока
    :return: символьный двумерный массив с буквами подсказки
    """

    best_hint = get_empty_board(15, 15)  # Создаем пустую доску

    for row in get_marked_rows(board):
        # Идем по строкам
        pass

    for row in get_marked_rows(transpose_board(board)):
        # Идем по столбцам
        pass

    return best_hint


# author - Pavel
def get_best_hint_for_empty_board(board: [[str]], letters: Counter) -> [[str]]:
    """
    Дает лучшую подсказку для первого хода (пустая доска)
    :param board: доска, на которой идет игра
    :param letters: буквы, которые есть у игрока
    :return: доска с лучшим словом
    """

    mid_index = int(len(board[0]) / 2)  # 7 for standard board

    # параметры лучшей подсказки
    #
    best_word = ""  # слово
    best_hint_value = 0  # цена
    best_hint_start_index = mid_index  # стартовый индекс

    # открываем словарь
    with open(DICTIONARY_FILENAME, 'r', encoding='utf-8') as dictionary:
        for line in dictionary:  # Читаем строки из словаря
            word = line[:-1]  # без \n
            # если слово нельзя собрать - пропускаем его
            if not is_word_compilable(letters, word):
                continue

            # размещаем слово по всем разрешенным позициям
            for i in range(mid_index - len(word) + 1, mid_index + 1):
                # считаем его ценность
                value = calculate_word_value(word, board, mid_index, i)
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

    return best_hint


# author - Matvey
def is_word_compilable(letters: Counter, word: str) -> bool:
    """
    Проверяет возможность составить слово из переданных букв.
    :param letters: счетчик букв игрока
    :param word: слово
    :return: можно ли составить из переданных букв переданое слово
    """

    word_letters = Counter(word)  # Счетчик букв для слова
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            # Если количество букв у игрока меньше, чем букв в слове
            return False
    return True


# author - Matvey
def get_regex_patterns(sharped_row: [str]) -> ([re.Pattern], [[str]]):
    """
    Получает строку, возвращает паттерны, соответствующие этой строке,
    для поиска подходящих слов в словаре по этому паттерну.
    :param sharped_row: размеченный '#' ряд
    :return: шаблоны, по которому можно найти подходящие слова и список для
    каждого шаблона, где находятся буквы из этого шаблона
    """
    prepared_row = []
    patterns = []
    letters = []
    letters_in_patterns = []
    # test_row = ['', '', '', 'а', '#', 'а', '#',
    # '#', '#', '#', '', 'р', '', '', '']

    for cell in range(len(sharped_row)):
        if sharped_row[cell]:  # Если в клетке есть символ
            prepared_row.append(sharped_row[cell])
        else:  # Если клетка пустая
            prepared_row.append(' ')
            # fixme: переписать?

    prepared_row = ''.join(prepared_row).split('#')
    # Соединяем в строку и нарезаем на подстроки по '#'

    for i in range(len(prepared_row)):
        if len(prepared_row[i]) > 1:
            # отбираем подстроки длинее 1 символа
            patterns.append(prepared_row[i])

    for pattern in patterns:
        for i in pattern:
            if i.isalpha():
                letters.append(i)
        letters_in_patterns.append(letters)
        letters = []

    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace(' ', '[а-я]?')
    # В пустое место можно вписать любую букву букву а-я или не писать ничего
    # todo: Можно переписать регулярку c помощью одних фигурных скобок

    for i in range(len(patterns)):
        patterns[i] = '^(' + patterns[i] + ')$'
    # Чтобы регулярка не хватала слова,
    # которые удовлетворяют, но выходят за рамки.

    for i in range(len(patterns)):
        patterns[i] = re.compile(patterns[i])
    # Компилируем каждый паттерн в регулярное выражение
    # Upd. компиляция не понадобится. Но пока не удалять

    return patterns, letters_in_patterns


# author - Matvey
# todo: удалить?
# def calculate_letters_value(word: str) -> int:
#     """
#     Считает ценность слова, без учета бонусов.
#     :param word: слово, ценность которого нужно посчитать
#     :return: ценность слова, без учета бонусов
#     """
#     return sum([LETTERS_VALUES[letter] for letter in word])


# author - Pavel
def calculate_word_value(word: str, board: [[str]],
                         line_index: int, start_index: int) -> int:
    """
    Считает ценность слова, расположенного на доске,
    с учетом бонусов на доске в любых кол-вах.
    Не учитывает бонусы, которые уже были использованы.
    Если игрок доложил 7 букв - добавляет 15 баллов.
    :param word: слово, ценность которого нужно посчитать
    :param board: доска с текущей позицией
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
            if bonus == "x2":
                letter_value *= 2
            elif bonus == "x3":
                letter_value *= 3
            elif bonus == "X2":
                word_bonuses_2x_counter += 1
            elif bonus == "X3":
                word_bonuses_3x_counter += 1

        value += letter_value
    # Считаем все собранные бонусы за слово
    value *= 2 ** word_bonuses_2x_counter
    value *= 3 ** word_bonuses_3x_counter

    # Выложил разом 7 букв - получи 15 баллов
    if new_letters_counter == 7:
        value += 15

    return value


# author - Pavel
def get_marked_rows(board: [[str]]) -> [[str]]:
    """
    Меняет доску, помечая заблокированные клетки знаком #
    Если у клетки есть символы сверху или снизу, то клетка заблокирована
    Постобработка:
    Между двумя # пустое пространство - все клетки между ними #
    От начала до # пустое пространство - все клетки между ними #
    От # до конца пустое пространство - все клетки между ними #
    :param board: символьный двумерный массив доски
    :return: одномерный массив символов(строка) с заблокированными клетками
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
            elif row[row_index] != '':
                last_sharp_index = -1

            # если дошли до конца и между последним # и концом нет символов,
            # все клетки между ними помечаем #
            if row_index == (len(row) - 1) and last_sharp_index != -1:
                for j in range(last_sharp_index + 1, row_index + 1):
                    row[j] = '#'

        marked_board.append(row)  # добавляем строку к новой доске

    return marked_board


# authors - Matvey and Pavel
def transpose_board(board: [[str]]) -> [[str]]:
    """
    Транспонирует двумерный массив
    :param board: двумерный массив доски
    :return: транспонированный двумерный массив
    """
    return list(np.array(board).transpose())


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


# author - Matvey
# todo: у нас изменились пути, переписать
# todo: может вернуть не имя файла, а путь к нему?
def get_smallest_sub_dict(letters_in_pattern: [str]) -> str:
    """
    Выбирает из списка букв самую редкую
    и возвращает название подсловаря с этой буквой.
    :param letters_in_pattern: список букв, которые есть в паттерне
    :return: имя наименьшего словаря
    """

    min_sub_dict_name = ''  # Название наименьшего словаря
    min_sub_dict_size = Path(Path.cwd() / 'dictionary.txt').stat().st_size

    # Считываем название полного словаря
    for i in letters_in_pattern:  # Идем по буквам
        sub_dict_letter = str('letter' + str(ord(i) - 1071) + '.txt')
        # Получаем название подсловаря

        sub_dict_size = Path(Path.cwd() / 'sub-dictionaries' /
                             sub_dict_letter).stat().st_size
        # Получаем размер подсловаря

        # Если размер подсловаря меньше минимального
        if sub_dict_size < min_sub_dict_size:
            min_sub_dict_name = sub_dict_letter
            min_sub_dict_size = sub_dict_size

    return min_sub_dict_name


# ----- TESTS -----
if __name__ == '__main__':
    pass

    # test_board = [
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', 'т', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', 'о', '', '', '', '', ''],
    #     ['', '', '', 'п', 'о', 'c', 'е', 'л', 'о', 'к', '', '', '', '', ''],
    #     ['', '', '', 'а', '', 'а', '', '', '', '', '', 'р', '', '', ''],
    #     ['', '', '', 'п', '', 'д', 'о', 'м', '', 'я', '', 'е', '', '', ''],
    #     ['', '', '', 'а', '', '', '', 'а', 'з', 'б', 'у', 'к', 'а', '', ''],
    #     ['', '', '', '', '', 'с', 'о', 'м', '', 'л', '', 'а', '', '', ''],
    #     ['', '', '', 'я', 'м', 'а', '', 'а', '', 'о', '', '', '', '', ''],
    #     ['', '', '', '', '', 'л', '', '', '', 'к', 'и', 'т', '', '', ''],
    #     ['', '', '', '', 'с', 'о', 'л', 'ь', '', 'о', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    # ]

    # print(20 == calculate_word_value('тотем',
    #                                  transpose_board(test_board), 11, 10))
    # print(8 == calculate_word_value('дуло',
    #                                 transpose_board(test_board), 4, 1))
    # передаем транспонированную доску, тк слово написано по вертикали
    # если доска транспонирована - координаты меняются местами

    # test_marked_board = get_marked_rows(test_board)
    # for iii in range(len(test_marked_board)):
    #     print(test_marked_board[iii])
    # print(get_marked_row(test_board, 12))

    # empty_board = get_empty_board(len(test_board), len(test_board[0]))
    # print(get_best_hint_for_empty_board(empty_board, Counter('собака'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('салат'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('шалаш'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('суп'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абв'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абвг'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абвгд'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абвгде'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абвгдеж'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абвгдежз'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('абвгдежзи'))[7])
    # print(get_best_hint_for_empty_board(empty_board,
    #                                     Counter('уеаояижзфцшщъыьэю'))[7])
    # print(get_best_hint_for_empty_board(empty_board, Counter('аашаш'))[7])

    # TIME: 1.36 s ± 21.7 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

    # patterns_, letters_ = get_regex_patterns(
    #    ['', '', 'ж', 'а', '#', 'а', '#', '#', '#', '#', '', 'р', 'ю', '', ''])
    # print(patterns_, letters_)

    # print(get_smallest_sub_dict(letters_))
