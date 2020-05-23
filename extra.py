from pathlib import Path
import json


# author - Pavel
def is_symbol_letter(symbol: str) -> bool:
    """
    Проверяет, является ли символ буквой
    Считает и кириллицу, и латиницу
    Считает и прописные, и заглавные буквы
    :param symbol: символ
    :return: true - это буква
    """

    if symbol is None or symbol == '':
        return False
    else:
        return 65 <= ord(symbol) <= 90 or 97 <= ord(symbol) <= 122 or \
               1040 <= ord(symbol) <= 1071 or 1072 <= ord(symbol) <= 1131


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
