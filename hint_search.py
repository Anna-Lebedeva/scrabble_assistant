import numpy as np
import json
from pathlib import Path


def get_best_hint(board: [[str]], letters: dict) -> [[str]]:
    """
    Дает лучшую подсказку слова на доске
    :param board: символьный двумерный массив доски
    :param letters: dict с набором букв
    :return: символьный двумерный массив с буквами подсказки
    """


def mark_blocked_cells(board: [[str]]) -> [[str]]:
    """
    Помечает клетки, в которых не может быть букв знаком '#'.
    Если рядом с клеткой по вертикали и горизонтали есть хотя бы по фишке, клетка заблокирована
    :param board: символьный двумерный массив доски
    :return: тот же массив с помеченными заблокированными клетками
    """

    for y_index in range(15):
        for x_index in range(15):
            if board[y_index][x_index] == '':  # если клетка пуста
                x_block = False  # заблокирована ли клетка по горизонтали
                y_block = False  # заблокирована ли клетка по вертикали

                if y_index > 0:  # если есть пространство сверху
                    if board[y_index - 1][x_index] != '' and board[y_index - 1][x_index] != '#':
                        y_block = True
                if y_index < 14:  # если есть пространство снизу
                    if board[y_index + 1][x_index] != '' and board[y_index + 1][x_index] != '#':
                        y_block = True

                if x_index > 0:  # если есть пространство слева
                    if board[y_index][x_index - 1] != '' and board[y_index][x_index - 1] != '#':
                        x_block = True
                if x_index < 14:  # если есть пространство справа
                    if board[y_index][x_index + 1] != '' and board[y_index][x_index + 1] != '#':
                        x_block = True

                if x_block and y_block:
                    board[y_index][x_index] = '#'

                # if x_index > 0 and y_index > 0:
                #     if board[y_index][x_index - 1] and board[y_index - 1][x_index]:  # если есть слева-сверху
                #         if board[y_index][x_index - 1] != '#' and board[y_index - 1][x_index] != '#':
                #             board[y_index][x_index] = '#'
                #             continue
                #
                # if x_index < 14 and y_index > 0:
                #     if board[y_index][x_index + 1] and board[y_index - 1][x_index]:  # если есть справа-сверху
                #         if board[y_index][x_index + 1] != '#' and board[y_index - 1][x_index] != '#':
                #             board[y_index][x_index] = '#'
                #             continue
                #
                # if y_index < 14 and x_index < 14:
                #     if board[y_index + 1][x_index] and board[y_index][x_index + 1]:  # если есть снизу-справа
                #         if board[y_index - 1][x_index] != '#' and board[y_index][x_index + 1] != '#':
                #             board[y_index][x_index] = '#'
                #             continue
                #
                # if y_index < 14 and x_index > 0:
                #     if board[y_index + 1][x_index] and board[y_index][x_index - 1]:  # если есть снизу-слева
                #         if board[y_index + 1][x_index] != '#' and board[y_index][x_index - 1] != '#':
                #             board[y_index][x_index] = '#'
    return board


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


def read_json(filename: str) -> dict:
    """
    Считывает json-файл в dict
    :param filename: имя json-файла
    :return: считанный словарь
    """

    with open(file=Path(Path.cwd() / filename), mode='r', encoding='utf-8') as file:
        return dict(json.load(file))


def calculate_word_value(word: str, json_filename: str, start_position: int, end_position: int) -> int:
    """
    Считает ценность слова
    :param word: слово в виде строки
    :param json_filename: имя json-словаря с ценностью букв
    :param start_position: индекс позиции начала слова
    :param end_position: индекс позиции конца слова
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

    word_dict = read_json(json_filename)
    word = word.lower()  # lowercase
    value = 0
    for char in word:
        value += word_dict[char]
    return value


# if __name__ == "__main__":
    # print(calculate_word_value("собака", "letters_values.json"))

    # test_board = mark_blocked_cells([
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
    # ])
    #
    # for s in test_board:
    #     print(s)
