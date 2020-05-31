from collections import Counter
from pathlib import Path
import json
import cv2
import numpy as np


# author - Matvey
def is_word_compilable(word: str, letters: Counter) -> bool:
    """
    Проверяет возможность составить слово из переданных букв.
    :param word: слово
    :param letters: буквы, имеющиеся у игрока
    :return: можно ли составить из переданных букв переданое слово
    """

    word_letters = Counter(word)  # Счетчик букв для слова
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            # Если количество букв у игрока меньше, чем букв в слове
            return False
    return True


# author - Pavel
def is_symbol_russian_letter(symbol: str) -> bool:
    """
    Проверяет, является ли символ буквой
    Считает только кириллицу
    Считает и прописные, и заглавные буквы
    :param symbol: символ
    :return: true - это буква
    """

    if symbol is None or not symbol:
        return False
    else:
        return 1040 <= ord(symbol) <= 1071 or 1072 <= ord(symbol) <= 1131


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


# authors - Pavel, Matvey
def read_json_to_list(json_filename: str) -> [[str]]:
    """
    Считывает json-файл в list
    :param json_filename: имя json-файла
    :return: считанный список
    """

    with open(file=Path(Path.cwd() / json_filename), mode='r',
              encoding='utf-8') as file:
        return list(json.load(file))


# author - Pavel
# todo: переписать не на cv2
def read_image(path: str) -> np.ndarray:
    return cv2.imread(path)


# author - Pavel
# todo: переписать не на cv2
def write_image(img: np.ndarray, path: str):
    cv2.imwrite(path, img)
