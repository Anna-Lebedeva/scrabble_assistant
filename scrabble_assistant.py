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


def mark_blocked_cells(board: [[str]]) -> [str]:
    """
    Помечает клетки, в которых не может быть букв знаком '#'.
    Если рядом с клеткой по вертикали и горизонтали есть буквы, то клетка заблокирована
    :param board: символьный двумерный массив доски
    :return: тот же массив с помеченными заблокированными клетками
    """

    for y_index in range(15):
        for x_index in range(15):
            if not board[y_index][x_index]:  # если клетка пуста
                x_block = False  # заблокирована ли клетка по горизонтали
                y_block = False  # заблокирована ли клетка по вертикали

                if y_index > 0:  # если есть пространство сверху
                    if not board[y_index - 1][x_index] and \
                            board[y_index - 1][x_index] != '#':
                        y_block = True
                if y_index < 14:  # если есть пространство снизу
                    if not board[y_index + 1][x_index] and \
                            board[y_index + 1][x_index] != '#':
                        y_block = True

                if x_index > 0:  # если есть пространство слева
                    if not board[y_index][x_index - 1] and \
                            board[y_index][x_index - 1] != '#':
                        x_block = True
                if x_index < 14:  # если есть пространство справа
                    if not board[y_index][x_index + 1] and \
                            board[y_index][x_index + 1] != '#':
                        x_block = True

                if x_block and y_block:
                    board[y_index][x_index] = '#'

    return board


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

    letters_values = read_json(json_filename)
    word = word.lower()  # перевод в нижний регист
    return sum([letters_values[letter] for letter in word])


def generate_regexs(row: [str]) -> [re.Pattern]:
    """
    Получает строку, возвращает паттерны, соответствующие этой строке, для поиска подходящих
    слов в словаре по этому паттерну
    :param s:
    :return: шаблон, по которому можно найти подходящие слова
    """
    patterns = []
    test_row = ['', '', '', 'а', '#', 'а', '#', '#', '#', '#', '', 'р', '', '', '']

    for cell in range(len(row)):
        if not row[cell]:  # если клетка пустая
            row[cell] = ' '

    row = ''.join(row).split('#')  # соединяем в строку и нарезаем на подстроки по '#'

    for i in range(len(row)):
        if len(row[i]) > 1:
            patterns.append(row[i])  # отбираем подстроки длинее 1 символа

    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace(' ', '[а-я]{,1}')
    # в пустое место можно вписать любую букву букву а-я или не писать ничего
    # todo: Можно переписать регулярку c помощью одних фигурных скобок

    for i in range(len(patterns)):
        if patterns[i][0] != '[':  # если начинается с буквы
            patterns[i] = '^' + patterns[i]
        if patterns[i][-1] != '}':  # если заканчивается буквой
            patterns[i] += '$'
    # чтобы регулярка не хватала слова, которые удовлетворяют, но выходят за рамки
    # работает, только если проверям строку из одного слова.

    for i in range(len(patterns)):
        patterns[i] = re.compile(patterns[i])
    # компилируем каждый паттерн в регулярное выражение

    return patterns

    # test
    """res = []
    for pattern in patterns:
        res.append(pattern.findall('''арка regd vbevu vy
                                   bjjk vbjjnk vbjki аркан'''))"""

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
#     letters_sum = read_json('letters_number.json')
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

    word_letters = Counter(word)
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            return False
    return True

# if __name__ == "__main__":
#     print(calculate_word_value("собака", "letters_values.json"))
#
#     test_board = mark_blocked_cells([
#         ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
#         ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
#         ['', '', '', '', '', '', '', '', '', 'т', '', '', '', '', ''],
#         ['', '', '', '', '', '', '', '', '', 'о', '', '', '', '', ''],
#         ['', '', '', 'п', 'о', 'c', 'е', 'л', 'о', 'к', '', '', '', '', ''],
#         ['', '', '', 'а', '', 'а', '', '', '', '', '', 'р', '', '', ''],
#         ['', '', '', 'п', '', 'д', 'о', 'м', '', 'я', '', 'е', '', '', ''],
#         ['', '', '', 'а', '', '', '', 'а', 'з', 'б', 'у', 'к', 'а', '', ''],
#         ['', '', '', '', '', 'с', 'о', 'м', '', 'л', '', 'а', '', '', ''],
#         ['', '', '', 'я', 'м', 'а', '', 'а', '', 'о', '', '', '', '', ''],
#         ['', '', '', '', '', 'л', '', '', '', 'к', 'и', 'т', '', '', ''],
#         ['', '', '', '', 'с', 'о', 'л', 'ь', '', 'о', '', '', '', '', ''],
#         ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
#         ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
#         ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
#     ])
#
#     for s in test_board:
#         print(s)
