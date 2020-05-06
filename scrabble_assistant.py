import numpy as np
import json
import re
from pathlib import Path
from collections import Counter


def get_best_hint(board: [[str]], letters: dict) -> [[str]]:
    """
    Дает лучшую подсказку слова на доске
    :param board: символьный двумерный массив доски
    :param letters: dict с набором букв
    :return: символьный двумерный массив с буквами подсказки
    """


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
                # если уже встречали # и до между текущим # и прошлым не было
                # символов, помечаем # все клетки между ними
                else:
                    for j in range(last_sharp_index + 1, row_index):
                        row[j] = '#'
                    last_sharp_index = row_index
            # если нашли какой-то символ, сбрасываем счетчик
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
    Искать слова удобнее в строке, а не в столбце. Переводит столбцы в строки.
    :param board: символьный двумерный массив доски
    :return: транспонированная матрица
    """

    return list(np.array(board).transpose())


def is_word_fits(vector: [str], word: str, start_position: int, end_position: int) -> bool:
    """
    Проверяет подходит ли слово в линию
    :param vector: символьный одномерный массив со специальными символами в заблокированных клетках
    :param word: слово в виде строки
    :param start_position: индекс позиции начала слова
    :param end_position: индекс позиции конца слова
    :return: true - слово подходит, false - слово не подходит
    """


def read_json(json_filename: str) -> dict:
    """
    Считывает json-файл в dict
    :param json_filename: имя json-файла
    :return: считанный словарь
    """

    with open(file=Path(Path.cwd() / 'jsons' / json_filename), mode='r',
              encoding='utf-8') as file:
        return dict(json.load(file))


def calculate_word_value(word: str, json_filename: str, board_bonuses_filename=0) -> int:
    # start_pos=: int, end_pos: int) -> int:
    """
    Считает ценность слова
    :param word: слово в виде строки
    :param json_filename: путь к json-словарю с ценностью букв
    :param cell_bonuses_filepath: путь к файлу с бонусами клеток
    # :param start_position: индекс позиции начала слова
    # :param end_position: индекс позиции конца слова
    :return: ценность слова
    """

    # разметка ценности полей доски:
    # 0 - обычное поле
    # 1 - х2 за букву
    # 2 - х3 за букву
    # 3 - х2 за слово
    # 4 - х3 за слово
    # 5 - стартовое поле

    board_values = [[4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],
                    [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
                    [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
                    [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
                    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                    [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
                    [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
                    [4, 0, 0, 1, 0, 0, 0, 5, 0, 0, 0, 1, 0, 0, 4],  # центр
                    [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
                    [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
                    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                    [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
                    [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
                    [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
                    [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],
                    ]

    letters_values = read_json(json_filename)
    word = word.lower()  # перевод в нижний регист
    return sum([letters_values[letter] for letter in word])


def get_regex_patterns(row: [str]) -> [re.Pattern]:
    """
    Получает строку, возвращает паттерны, соответствующие этой строке, для поиска подходящих
    слов в словаре по этому паттерну.
    :param row: размеченный '#' ряд
    :return: шаблон, по которому можно найти подходящие слова
    """
    prepared_row = []
    patterns = []
    test_row = ['', '', '', 'а', '#', 'а', '#', '#', '#', '#', '', 'р', '', '', '']

    for cell in range(len(row)):
        if row[cell]:  # если в клетке есть символ
            prepared_row[cell] = row[cell]
        else:  # если клетка пустая
            prepared_row[cell] = ' '

    prepared_row = ''.join(prepared_row).split('#')
    # соединяем в строку и нарезаем на подстроки по '#'

    for i in range(len(prepared_row)):
        if len(prepared_row[i]) > 1:
            patterns.append(prepared_row[i])  # отбираем подстроки длинее 1 символа

    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace(' ', '[а-я]{,1}')
    # в пустое место можно вписать любую букву букву а-я или не писать ничего
    # todo: Можно переписать регулярку c помощью одних фигурных скобок

    for i in range(len(patterns)):
        if patterns[i][0] != '[':  # если начинается с буквы
            patterns[i] = '^' + patterns[i]
        if patterns[i][-1] != '}':  # если заканчивается буквой
            patterns[i] += '$'
    # Чтобы регулярка не хватала слова, которые удовлетворяют, но выходят за рамки.
    # Работает корректно, только если в строке одно слово.

    for i in range(len(patterns)):
        patterns[i] = re.compile(patterns[i])
    # компилируем каждый паттерн в регулярное выражение

    return patterns


def is_word_correct(word: str, json_filename: str) -> bool:
    """
    Проверяет слово на корректность - не содержит ли оно неожиданных символов,
    не содержит ли оно больше букв, чем есть в игре.
    :param word: слово
    :param json_filename: имя json-словаря с ценностью букв
    :return: переданное слово не содержит неожиданных символов
    """
    # todo: добавить поправку на бонусы

    word = word.lower()
    alphabet = set(
        read_json(json_filename).keys())  # множество букв, для которых указана стоимость

    for letter in word:
        if letter not in alphabet:
            return False

    letters_sum = read_json('letters_amount.json')
    word_letters = Counter(word)

    for letter in word:
        if word_letters[letter] > letters_sum[letter]:
            return False
    return True


def is_word_available(letters: Counter, word: str) -> bool:
    """
    Проверяет возможность составить слово из переданных букв
    :param letters: счетчик букв игрока
    :param word: слово
    :return: можно ли составить из переданных букв переданое слово
    """

    word_letters = Counter(word)  # счетчик букв
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            return False
    return True


if __name__ == "__main__":
    test_board = [
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', 'т', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', 'о', '', '', '', '', ''],
        ['', '', '', 'п', 'о', 'c', 'е', 'л', 'о', 'к', '', '', '', '', ''],
        ['', '', '', 'а', '', 'а', '', '', '', '', '', 'р', '', '', ''],
        ['', '', '', 'п', '', 'д', 'о', 'м', '', 'я', '', 'е', '', '', ''],
        ['', '', '', 'а', '', '', '', 'а', 'з', 'б', 'у', 'к', 'а', '', ''],
        ['', '', '', '', '', 'с', 'о', 'м', '', 'л', '', 'а', '', '', ''],
        ['', '', '', 'я', 'м', 'а', '', 'а', '', 'о', '', '', '', '', ''],
        ['', '', '', '', '', 'л', '', '', '', 'к', 'и', 'т', '', '', ''],
        ['', '', '', '', 'с', 'о', 'л', 'ь', '', 'о', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    ]
    # test_board = transpose_board(test_board)

    test_marked_board = get_marked_rows(test_board)
    for i in range(len(test_marked_board)):
        print(test_marked_board[i])
    # print(get_marked_row(test_board, 12))
