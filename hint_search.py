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


def mark_blocked_cells(board_letters: [[str]]) -> [[str]]:
    """
    Помечает клетки, в которых не может быть букв знаком '#'.

    :param board_letters: принимает распознанную символьную сетку
    :return: возвращает распознанную символьную сетку с помеченными заблокированными клетками
    """

    # пример распознаной доски, переданной на вход:
    board_letters = [
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

    for ver_char in range(15):
        for hor_char in range(15):
            if not board_letters[ver_char][hor_char]:  # находит пустую клетку

                if hor_char > 0 and ver_char > 0:
                    if board_letters[ver_char][hor_char - 1] and \
                            board_letters[ver_char - 1][hor_char]:  # если есть слева-сверху
                        if board_letters[ver_char][hor_char - 1] != '#' and \
                                board_letters[ver_char - 1][hor_char] != '#':
                            board_letters[ver_char][hor_char] = '#'
                            continue

                if hor_char < 14 and ver_char > 0:
                    if board_letters[ver_char][hor_char + 1] and \
                            board_letters[ver_char - 1][hor_char]:  # если есть справа-сверху
                        if board_letters[ver_char][hor_char + 1] != '#' and \
                                board_letters[ver_char - 1][hor_char] != '#':
                            board_letters[ver_char][hor_char] = '#'
                            continue

                if ver_char < 14 and hor_char < 14:
                    if board_letters[ver_char + 1][hor_char] and \
                            board_letters[ver_char][hor_char + 1]:  # если есть снизу-справа
                        if board_letters[ver_char - 1][hor_char] != '#' and \
                                board_letters[ver_char][hor_char + 1] != '#':
                            board_letters[ver_char][hor_char] = '#'
                            continue

                if ver_char < 14 and hor_char > 0:
                    if board_letters[ver_char + 1][hor_char] and \
                            board_letters[ver_char][hor_char - 1]:  # если есть снизу-слева
                        if board_letters[ver_char + 1][hor_char] != '#' and \
                                board_letters[ver_char][hor_char - 1] != '#':
                            board_letters[ver_char][hor_char] = '#'
    return board_letters


def get_horizontal_from_vertical(board: [[str]]) -> [[str]]:
    """
    Искать слова убоднее в строке, а не в столбце. Переводит столбцы в строки.

    :param board: символьный двумерный массив доски
    :return: массив вертикалей, переведенный в массив горизонталей (транспонированную матрицу)
    """

    return np.array(board).transpose()


def is_word_fits(line: [str], word: str, start_position: int,
                 end_position: int) -> bool:
    """
    Проверяет подходит ли слово в линию
    :param line: символьный одномерный массив со специальными символами в заблокированных клетках
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


def calculate_word_value(word: str, json_filename: str) -> int:
    """
    Считает ценность слова
    :param word: слово в виде строки
    :param json_filename: имя json-словаря
    :return: ценность слова
    """

    word_dict = read_json(json_filename)
    word = word.lower()  # lowercase
    value = 0
    for char in word:
        value += word_dict[char]
    return value


if __name__ == "__main__":
    print(calculate_word_value("собака", "letters_values.json"))
    print(mark_blocked_cells([
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
    ]))
