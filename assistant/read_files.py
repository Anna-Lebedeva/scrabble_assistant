from pathlib import Path
import json
import cv2
import numpy as np


# author - Matvey
def read_json_to_dict(json_path: str) -> dict:
    """
    Считывает json-файл в dict
    :param json_path: имя json-файла
    :return: считанный словарь
    """

    with open(file=Path(Path.cwd() / json_path), mode='r',
              encoding='utf-8') as file:
        return dict(json.load(file))


# authors - Pavel, Matvey
def read_json_to_list(json_path: str) -> [[str]]:
    """
    Считывает json-файл в list
    :param json_path: имя json-файла
    :return: считанный список
    """

    with open(file=Path(Path.cwd() / json_path), mode='r',
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
