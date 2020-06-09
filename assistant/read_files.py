from pathlib import Path
import json
import cv2
import numpy as np


# author - Matvey
def read_json_to_dict(json_path: Path) -> dict:
    """
    Считывает json-файл в dict
    :param json_path: имя json-файла
    :return: считанный словарь
    """

    with open(file=Path(Path.cwd() / json_path), mode='r',
              encoding='utf-8') as file:
        return dict(json.load(file))


# authors - Pavel, Matvey
def read_json_to_list(json_path: Path) -> [[str]]:
    """
    Считывает json-файл в list
    :param json_path: имя json-файла
    :return: считанный список
    """

    with open(file=Path(Path.cwd() / json_path), mode='r',
              encoding='utf-8') as file:
        return list(json.load(file))


# author - Pavel
def read_image(path: str) -> np.ndarray:
    return cv2.imread(path)


# author - Pavel
def write_image(img: np.ndarray, path: str):
    cv2.imwrite(path, img)
