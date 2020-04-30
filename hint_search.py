import json
from pathlib import Path


def read_char_values(filename: str) -> dict:
    """
    Считывает цену каждой буквы из json-файла. Возвращает словарь с ценами для каждой буквы.
    Использутся в качестве аргумента для word_to_values.

    :param filename: имя json-файла в текущей директории, откуда считываются цены букв
    :return: словарь, где по букве находится ее цена
    """
    with open(
            file=Path(Path.cwd() / filename),
            mode='r', encoding='utf-8') as file:
        return dict(json.load(file))


def word_to_value(word: str, char_values: dict) -> int:
    """
    :param word: слово, для которого рассчитывается его суммарная цена
    :param char_values: словарь с ценами букв
    :return: цена слова для переданного слова, при переданных ценах букв
    """
    word = word.lower()
    value = 0
    for char in word:
        value += char_values[char]
    return value
