# Scrabble assistant (Помощник для игры Эрудит)
Распознавание доски и получение подсказок по фотографии в настольной игре Scrabble (Эрудит)

Работоспособность на операционных системах, 
отличных от Windows 10, не гарантируется.

**Open README_ENG.md for instructions in English.**

## Необходимые пакеты:
- [Python 3.7.7](https://www.python.org/)
- [TensorFlow 2.2.0](https://www.tensorflow.org/)
- [Keras 2.3.1](https://keras.io/)
- [Pillow 7.1.2](https://python-pillow.org/)
- [Imutils 0.5.3](https://github.com/jrosebr1/imutils)
- [PyQt5 5.14.2](https://pypi.org/project/PyQt5/)
- [Pandas 1.0.4](https://pandas.pydata.org/)

Установить одной командой:
```commandline
pip install -r requirements.txt
```
## Как с этим работать
#### Подготовка датасета (preprocessing/dataset_preprocessing.py)
Для начала необходимо собрать фотографии доски с фишками, 
расставленными по алфавиту следующим образом:
![Доска для датасета](resources/for_readme/raw.jpg)  
От количества сделанных фотографий будет зависит качество предсказаний модели
(желательно сделать не менее 500).

Далее помещаем эти фотографии в одну папку, указываем путь до неё в
константе IMAGES_TO_CUT_PATH и запускаем скрипт. 
Результат окажется в папке, указанной DATASET_PATH. 
В CV/scan.py изменением значения константы IMG_SIZE настраивается размер 
фишек для датасета.

#### Тренировка