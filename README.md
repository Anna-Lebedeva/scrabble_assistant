# Scrabble assistant
Распознавание доски и получение подсказок по фотографии в настольной игре Scrabble (Эрудит)

## Необходимые пакеты:
- [Python 3.7.7](https://www.python.org/)
- [OpenCV-python 4.2.0.34](https://pypi.org/project/opencv-python/)
- [imageio 2.8.0](https://imageio.readthedocs.io/en/stable/installation.html)
- [Pandas 1.0.3](https://github.com/pandas-dev/pandas/releases)
- [Imutils 0.5.3](https://github.com/jrosebr1/imutils)
- [PyQt5 5.14.2](https://pypi.org/project/PyQt5/)
- [scikit-image 0.17.2](https://scikit-image.org/)
- [scikit-learn 0.22.2.post1](https://scikit-learn.org/stable/index.html)
- **...**

Весь список в requirements.txt. Установить одной командой:
```commandline
pip install -r requirements.txt
```
## Что сделано/не сделано

 - Есть:
   + Обрезка доски по внешнему и затем внутреннему контуру
   + Подготовка ячеек доски к дальнейшему использованию
   + Тренировка и распознавание
   + Удобное приложение
 - Нет:
   + Алгоритмов для звёздочки

## Как с этим работать
#### Подготовка датасета (preprocessing/dataset.py)
Для начала необходимо собрать фотографии доски с фишками, 
расставленными по алфавиту следующим образом:  
![Доска для датасета](resources/for_readme/raw.jpg)  
От количества сделанных фотографий будет зависит качество предсказаний модели.

Далее помещаем эти фотографии в одну папку, указываем путь до неё в 
IMAGES_TO_CUT_PATH и запускаем скрипт. Результат окажется в папке, 
указанной DATASET_PATH. В CV/scan.py IMG_SIZE настраиват 
размер фишек для датасета.

Датасет, подготовленный нами,
[тут](https://drive.google.com/file/d/1kW2adFPwH_PdxLksCwoUqIUF13CVfA8N/view?usp=sharing).

#### Тренировка (preprocessing/model.py)
Проверяем DATASET_PATH, запускаем и ждём результат.

#### Проверка результатов (for_testing.py)
Для тестирования подготовлен
[архив](https://drive.google.com/file/d/1uWUkDROoMkXpwo2WK2v2An2xRGBvoUoS/view?usp=sharing)
с разными игровыми ситуациями и освещением.

#### Приложение (app.py)
Запускаем приложение, загружаем фотографию доски с фишками 
(или пустую, если первый ход) и жмём "Найти". Подсказки 
(их количество задаётся _hints_amount) будут выведены на изображении 
обрезанной по внутреннему контуру доски, рядом с ними указана ценность.