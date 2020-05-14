import numpy as np
import json
from pathlib import Path
from collections import Counter

LETTERS_VALUES_FILENAME = "letters_values.json"
LETTERS_AMOUNT_FILENAME = "letters_amount.json"
BOARD_BONUSES_FILENAME = "board_bonuses.json"
DICTIONARY_FILENAME = "dictionary.txt"


def get_best_hint(board: [[str]], letters: Counter) -> [[str]]:
    """
    Дает лучшую подсказку слова на доске
    :param board: символьный двумерный массив доски
    :param letters: набор букв игрока
    :return: символьный двумерный массив с буквами подсказки
    """

    best_hint = board.copy()  # подсказка - отдельная доска

    # очищаем доску-подсказку
    for best_hint_y_index in range(len(best_hint)):
        for best_hint_x_index in range(len(best_hint[best_hint_y_index])):
            best_hint[best_hint_y_index][best_hint_x_index] = ''

    for row in get_marked_rows(board):
        # идем по строкам
        pass

    for row in get_marked_rows(transpose_board(board)):
        # идем по столбцам
        pass

    return best_hint


def get_regex_patterns(sharped_row: [str]) -> [str]:
    """
    Получает строку, возвращает паттерны, соответствующие этой строке,
    для поиска подходящих слов в словаре по этому паттерну.
    :param sharped_row: размеченный '#' ряд
    :return: шаблон, по которому можно найти подходящие слова
    """
    prepared_row = []
    patterns = []
    # test_row = ['', '', '', 'а', '#', 'а', '#',
    #             '#', '#', '#', '', 'р', '', '', '']

    for cell in range(len(sharped_row)):
        if sharped_row[cell]:  # если в клетке есть символ
            prepared_row.append(sharped_row[cell])
        else:  # если клетка пустая
            prepared_row.append(' ')

    prepared_row = ''.join(prepared_row).split('#')
    # соединяем в строку и нарезаем на подстроки по '#'

    for i in range(len(prepared_row)):
        if len(prepared_row[i]) > 1:
            # отбираем подстроки длинее 1 символа
            patterns.append(prepared_row[i])

    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace(' ', '[а-я]?')
    # в пустое место можно вписать любую букву букву а-я или не писать ничего
    # todo: Можно переписать регулярку c помощью одних фигурных скобок

    for i in range(len(patterns)):
        patterns[i] = '^(' + patterns[i] + ')$'
    # Чтобы регулярка не хватала слова, которые удовлетворяют,
    # но выходят за рамки.

    # for i in range(len(patterns)):
    #    patterns[i] = re.compile(patterns[i])
    # компилируем каждый паттерн в регулярное выражение
    # upd. компиляция не понадобится. Но пока не удалять

    return patterns


def calculate_word_value(word: str, line_index: int, start_pos: int) -> int:
    """
    Считает ценность слова, расположенного на доске
    Учитывает стоимость буквы и бонусы на доске в любых кол-вах
    :param word: слово в виде строки
    :param line_index: индекс строки, в которой стоит слово
    :param start_pos: индекс начала слова в строке
    :return: ценность слова
    """

    # разметка ценности полей доски:
    # 00 - обычное поле
    # x2 - х2 за букву
    # x3 - х3 за букву
    # X2 - х2 за слово
    # X3 - х3 за слово
    # ST - стартовое поле

    # ценность букв как словарь
    letters_values = read_json_to_dict(LETTERS_VALUES_FILENAME)

    # бонусы на доске как массив
    board_bonuses = read_json_to_list(BOARD_BONUSES_FILENAME)

    value = 0
    word_bonuses_2x_counter = 0  # сколько бонусов x2 слово собрали
    word_bonuses_3x_counter = 0  # сколько бонусов x3 слово собрали
    for i in range(len(word)):  # идем по символам слова
        letter = word[i]
        # изначальная ценность буквы без бонусов
        letter_value = letters_values[letter]

        # бонус на клетке, где стоит буква
        bonus = board_bonuses[line_index][start_pos + i]
        if bonus == "x2":
            letter_value *= 2
        elif bonus == "x3":
            letter_value *= 3
        elif bonus == "X2":
            word_bonuses_2x_counter += 1
        elif bonus == "X3":
            word_bonuses_3x_counter += 1
        value += letter_value
    # считаем все собранные бонусы за слово
    value = value * pow(2, word_bonuses_2x_counter)
    value = value * pow(3, word_bonuses_3x_counter)

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
    :param board: символьный двумерный массив доски
    :return: транспонированный двумерный массив
    """
    return list(np.array(board).transpose())


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


if __name__ == '__main__':
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
    # test_board = transpose_board(test_board)

    # test_marked_board = get_marked_rows(test_board)
    # for iii in range(len(test_marked_board)):
    #     print(test_marked_board[iii])
    # print(get_marked_row(test_board, 12))
    print(calculate_word_value("сахар", 5, 5))
