import json
from collections import Counter
from pathlib import Path
import re

import numpy as np

LETTERS_VALUES_FILENAME = "letters_values.json"
LETTERS_AMOUNT_FILENAME = "letters_amount.json"
BOARD_BONUSES_FILENAME = "board_bonuses.json"
DICTIONARY_FILENAME = "dictionary.txt"


def read_json_to_dict(json_filename: str) -> dict:
    """
    Считывает json-файл в dict
    :param json_filename: имя json-файла
    :return: считанный словарь
    """
    with open(file=Path(Path.cwd() / 'jsons' / json_filename), mode='r',
              encoding='utf-8') as file:
        return dict(json.load(file))


def read_json_to_list(json_filename: str) -> [[str]]:
    """
    Считывает json-файл в list
    :param json_filename: имя json-файла
    :return: считанный массив
    """
    with open(file=Path(Path.cwd() / 'jsons' / json_filename), mode='r',
              encoding='utf-8') as file:
        return list(json.load(file))


def read_txt_to_list(txt_filename: str) -> [str]:
    """
    Возвращает список слов, из словаря с указанным названием.
    :param txt_filename: название словаря
    :return: список слов, из словаря с указанным названием
    """
    words = []
    with open(Path(Path.cwd() / 'dictionaries' / txt_filename), mode='r',
              encoding='utf-8') as txt_file:
        for line in txt_file:
            words.append(line[:-1])
    return words


LETTERS_VALUES = read_json_to_dict(LETTERS_VALUES_FILENAME)
LETTERS_AMOUNT = read_json_to_dict(LETTERS_AMOUNT_FILENAME)
BOARD_BONUSES = read_json_to_list(BOARD_BONUSES_FILENAME)


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


def get_best_hint_for_empty_board(board: [[str]], letters: Counter) -> [[str]]:
    """
    Генерирует первый ход. Выдает расположение лучшего слова для 1-ого хода.
    :param board: доска, на которой идет игра
    :param letters: буквы, которые есть у игрока
    :return: доска с расположенным лучшим словом
    """

    mid_index = int(len(board) / 2)  # центральная клетка по x

    # далее определяем bonus_range, используя файл с бонусами
    # при bones_range = len(letters) и выше, бонусы не учитываются
    # в стандартном случае при len(letters) = 7 бонусы не учтутся
    bonus_range = 7  # расстояние между центром и бонусами
    for i in range(mid_index + 1, len(BOARD_BONUSES[mid_index])):
        if BOARD_BONUSES[mid_index][i] == "x2":
            bonus_range = i - mid_index
            break

    best_word = ""  # лучшее слово
    best_hint = get_empty_board(len(board), len(board[0]))  # лучшее слово
    # в формате матрицы
    best_hint_value = 0  # ценность лучшего слова
    best_hint_start_index = mid_index  # стартовая позиция лучшего слова

    dictionary = read_txt_to_list("dictionary.txt")

    # идем по словарю
    for word in dictionary:
        # если можем составить слово из тех букв, что имеются
        if is_word_compilable(letters, word):

            # если слово слишком короткое для бонуса
            if len(word) <= bonus_range:
                # считаем ценность слова
                word_value = calculate_word_value(word, board, mid_index,
                                                  mid_index - 1)
                # если ценность выше текущего лучшего слова,
                # берем новое слово за самое ценное
                if word_value >= best_hint_value:
                    best_word = word
                    best_hint_value = word_value
                    best_hint_start_index = mid_index - 1

            # если слово может попасть на бонус
            else:
                # идем по позициям слева так, чтобы зацепить бонус,
                # но также зацепить стартовую клетку
                for i in range(mid_index - len(word) + 1,
                               mid_index - bonus_range + 1):
                    # считаем ценность слова
                    word_value = calculate_word_value(word, board, mid_index, i)

                    # если ценность выше текущего лучшего слова,
                    # берем новое слово за самое ценное
                    if word_value >= best_hint_value:
                        best_word = word
                        best_hint_value = word_value
                        best_hint_start_index = i

                    # далее то же самое для симметричной позиции

                    # симметричный i индекс
                    sym_index = 2 * mid_index - i - len(word) + 1
                    word_value = calculate_word_value(word, board, mid_index,
                                                      sym_index)
                    if word_value >= best_hint_value:
                        best_word = word
                        best_hint_value = word_value
                        best_hint_start_index = sym_index

    # записываем полученные результаты в матрицу
    for i in range(len(best_word)):
        best_hint[mid_index][best_hint_start_index + i] = best_word[i]

    return best_hint


def is_word_compilable(letters: Counter, word: str) -> bool:
    """
    Проверяет возможность составить слово из переданных букв.
    :param letters: счетчик букв игрока
    :param word: слово
    :return: можно ли составить из переданных букв переданое слово
    """
    # todo: Добавить передачу паттерна, чтобы искать с учетом буквы на доске

    word_letters = Counter(word)  # Счетчик букв для слова
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            # Если количество букв у игрока меньше, чем букв в слове
            return False
    return True


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


# def calculate_letters_value(word: str) -> int:
#     """
#     Считает ценность слова, без учета бонусов.
#     :param word: слово, ценность которого нужно посчитать
#     :return: ценность слова, без учета бонусов
#     """
#     return sum([LETTERS_VALUES[letter] for letter in word])


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


def transpose_board(board: [[str]]) -> [[str]]:
    """
    Транспонирует двумерный массив
    :param board: двумерный массив доски
    :return: транспонированный двумерный массив
    """
    return list(np.array(board).transpose())


def get_empty_board(y: int, x: int) -> [[str]]:
    """
    Генерирует пустую матрицу в y строк и x столбцов
    И заполняет ее символами пустыми строками
    :param y: кол-во строк
    :param x: кол-во столбцов
    :return: матрица y*x
    """
    return [[''] * y for _ in range(x)]


def get_smallest_sub_dict(letters_in_patterns: [[str]]) -> [str]:
    """
    Для каждого паттерна находит подсловарь наименьшего размера,
    где содержатся все подходящие в паттерн слова.
    :param letters_in_patterns: список со списками букв для каждого паттерна
    :return: список с названиями подсловарей
    наименьшего размера для каждого паттерна.
    """
    sub_dicts = []

    for letters in letters_in_patterns:
        min_sub_dict = ''  # название наименьшего словаря
        min_sub_dict_size = Path(Path.cwd() / 'dictionary.txt').stat().st_size
        for i in letters:
            sub_dict_letter = str('letter' + str(ord(i) - 1071) + '.txt')
            sub_dict_size = Path(Path.cwd() / 'sub-dictionaries' /
                                 sub_dict_letter).stat().st_size
            if sub_dict_size < min_sub_dict_size:
                min_sub_dict = sub_dict_letter
                min_sub_dict_size = sub_dict_size
        sub_dicts.append(min_sub_dict)

    return sub_dicts


# ----- TESTS -----
if __name__ == '__main__':
    pass
    # test_board = [
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    # ]

    # print(get_best_hint_for_empty_board(test_board, Counter('собака'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('салатик'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('шалаш'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('суп'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абв'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абвг'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абвгд'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абвгде'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абвгдеж'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абвгдежз'))[7])
    # print(get_best_hint_for_empty_board(test_board, Counter('абвгдежзи'))[7])
    # print(get_best_hint_for_empty_board(test_board,
    # Counter('уеаояижзфцшщъыьэю'))[7])
