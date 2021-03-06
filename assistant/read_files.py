from pathlib import Path
import json


# author: Matvey
def read_json_to_dict(json_path: Path) -> dict:
    """
    Считывает json-файл в dict
    :param json_path: имя json-файла
    :return: считанный словарь
    """

    with open(file=Path(Path.cwd() / json_path), mode='r',
              encoding='utf-8') as file:
        return dict(json.load(file))


# authors: Matvey, Pavel
def read_json_to_list(json_path: Path) -> [[str]]:
    """
    Считывает json-файл в list
    :param json_path: имя json-файла
    :return: считанный список
    """

    with open(file=Path(Path.cwd() / json_path), mode='r',
              encoding='utf-8') as file:
        return list(json.load(file))
