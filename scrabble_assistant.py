import numpy as np
import json
from pathlib import Path
from collections import Counter


def get_best_hint(board: [[str]], letters: dict) -> [[str]]:
    """
    Дает лучшую подсказку слова на доске
    :param board: символьный двумерный массив доски
    :param letters: dict с набором букв
    :return: символьный двумерный массив с буквами подсказки
    """


def get_marked_row(board: [[str]], index: int) -> [str]:
    """
    Извлекает i-тый вектор из доски, помечая заблокированные клетки знаком #
    Если у клетки есть символы сверху или снизу, то клетка заблокирована
    :param board: символьный двумерный массив доски
    :param index: индекс строки в массиве
    :return: одномерный массив символов(строка) с заблокированными клетками
    """

    row = board[index].copy()  # i-тая строка доски
    for i in range(len(row)):
        up_block = False  # заблокировано ли сверху
        down_block = False  # заблокировано ли снизу

        if not row[i]:  # если в клетке пусто
            if index > 0:
                if board[index - 1][i]:
                    up_block = True
            if index < 14:
                if board[index + 1][i]:
                    down_block = True
            if up_block or down_block:
                row[i] = '#'

    return row


def transpose_board(board: [[str]]) -> [[str]]:
    """
    Искать слова удобнее в строке, а не в столбце. Переводит столбцы в строки.
    :param board: символьный двумерный массив доски
    :return: транспонированная матрица
    """

    return np.array(board).transpose()


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

    with open(file=Path(Path.cwd() / 'jsons' / json_filename), mode='r', encoding='utf-8') as file:
        return dict(json.load(file))


def calculate_word_value(word: str, json_filename: str, cell_bonuses_filepath: str) -> int:
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

    letter_values = read_json(json_filename)
    word = word.lower()  # перевод в нижний регистр
    value = 0
    for char in word:
        value += letter_values[char]
    return value


# def is_word_correct(word: str, json_filename: str) -> bool:
#     """
#     Проверяет слово на корректность - не содержит ли оно неожиданных символов,
#     не содержит ли оно больше букв, чем есть в игре.
#     :param word: слово
#     :param json_filename: имя json-словаря с ценностью букв
#     :return: переданное слово не содержит неожиданных символов
#     """
#     word = word.lower()
#     alphabet = set(
#         read_json(json_filename).keys())  # множество букв, для которых указана стоимость
#     for letter in word:
#         if letter not in alphabet:
#             return False
#
#     letters_sum = read_json('letters_amount.json')
#     word_letters = Counter(word)
#
#     for letter in word:
#         if word_letters[letter] > letters_sum[letter]:
#             return False
#     return True


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

    for j in range(14):
        print(get_marked_row(test_board, j))
    # print(get_marked_vector(test_board, 6))
