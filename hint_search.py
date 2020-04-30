import json
from pathlib import Path


def get_best_hint(board: [[str]], letters: dict) -> [[str]]:
    """
    Дает лучшую подсказку слова на доске
    :param board: символьный двумерный массив доски
    :param letters: dict с набором букв
    :return: символьный двумерный массив с буквами подсказки
    """


def get_vertical_by_index(board: [[str]], index: int) -> [str]:
    """
    Возвращает вертикаль со специальными символами в заблокированных клетках
    :param board: символьный двумерный массив доски
    :param index: индекс нужной вертикали
    :return: одномерный массив
    """


def get_horizontal_by_index(board: [[str]], index: int) -> [str]:
    """
    Возвращает горизонталь со специальными символами в заблокированных клетках
    :param board: символьный двумерный массив доски
    :param index: индекс нужной вертикали
    :return: одномерный массив
    """


def is_word_fits(line: [str], word: str, start_position: int, end_position: int) -> bool:
    """
    Проверяет подходит ли слово в линию
    :param line: символьный одномерный массив со специальными символами в заблокированных клетках
    :param word: слово в виде строки
    :param start_position: индекс позиции начала слова
    :param end_position: индекс позиции конца слова
    :return: true - слово подходит, false - слово не подходит
    """


# def clean_file(filename_in: str, filename_out: str, n: int) -> None:
#     """
#     Очищает txt словарь от слов, где более n символов
#     path_in и path_out могут быть равны
#     :param filename_in: имя файла на вход
#     :param filename_out: имя файла на выход
#     :param n: максимально допустимая длина слова
#     """
#
#     if filename_in == filename_out:
#         words = []
#         f = open(filename_in, "r")
#         for i in f.readlines():
#             if len(i) <= n + 1:  # "\n" тоже учитывается, поэтому +1
#                 words.append(i)
#         f.close()
#         f = open(filename_in, "w")
#         for i in words:
#             f.write(i)
#     else:
#         f_in = open(filename_in, "r")
#         f_out = open(filename_out, "w")
#
#         for i in f_in.readlines():
#             if len(i) <= n + 1:  # "\n" тоже учитывается, поэтому +1
#                 f_out.write(i)
#         f_in.close()
#         f_out.close()


def read_json(filename: str) -> dict:
    """
    Считывает json-файл в dict
    :param filename: имя json-файла
    :return: dict
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
