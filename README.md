# Scrabble assistant
Распознавание доски и получение подсказок по фотографии в настольной игре Scrabble (Эрудит)

## Необходимые пакеты:
- [Python 3.7.7](https://www.python.org/)
- [OpenCV-python 4.2.0.34](https://pypi.org/project/opencv-python/)
- [imageio 2.8.0](https://imageio.readthedocs.io/en/stable/installation.html)
- [Pandas 1.0.3](https://github.com/pandas-dev/pandas/releases)
- [Pillow 7.1.2](https://python-pillow.org/)
- [Imutils 0.5.3](https://github.com/jrosebr1/imutils)
- [PyQt5 5.14.2](https://pypi.org/project/PyQt5/)
- **...**

Актуальный список в requirements.txt. Установить одной командой:
```commandline
pip install -r requirements.txt
```
## Как с этим работать
#### Подготовка датасета (preprocessing/dataset.py)
Для начала необходимо собрать фотографии доски с фишками, 
расставленными по алфавиту следующим образом:  
![Доска для датасета](resources/for_readme/raw.jpg)  
От количества сделанных фотографий будет зависит качество предсказаний модели.

Далее помещаем эти фотографии в одну папку, указываем путь до неё в 
IMAGES_TO_CUT_PATH и запускаем скрипт. Результат окажется в папке, 
указанной DATASET_PATH. IMG_SIZE настраиват размер фишек для датасета.

#### Тренировка
???