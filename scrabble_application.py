from collections import Counter

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon
import sys

from scrabble_assistant import *


# author - Pavel
class ScrabbleApplication(QWidget):

    # resolution of the window
    _width = 420
    _height = 800

    # изображения
    _board_img = 0  # изображение доски (фото)
    _icon_file_path = 'images/icon.png'
    _background_file_path = 'images/app_background.jpg'  # фоновое изображение

    # словари с буквами
    _LETTERS_AMOUNT = LETTERS_AMOUNT  # словарь с кол-вом букв в игре
    _letters_used = dict()   # словарь с кол-вом букв, которые уже есть на доске
    _letters_dict = dict()  # словарь с буквами, которые выбрал юзер

    # кнопки
    _letters_buttons = None  # кнопки с буквами 'А'-'Я' и '*'
    _drop_button = None  # кнопка 'сбросить счетчик букв'
    _get_hint_button = None  # кнопка 'завершить ввод'
    _upload_img_button = None  # кнопка 'сделать фото' / 'загрузить картинку'
    _start_button = None  # кнопка по нажатии запускает весь алгоритм

    # labels
    _msg = None
    _msg_start_caption = 'Выберите ваши буквы и загрузите фото доски'

    # размеры виджетов
    _cell_size = _width // 7  # размер кнопки с буквой в px
    _row_size = _cell_size * (_width // _cell_size)  # длина линии кнопок в px

    def __init__(self):
        super().__init__()

        self.init_dict()
        self.init_buttons()
        self.init_labels()
        self.init_ui()
        self.draw_widgets()

    def init_ui(self):
        """
        Инициализация окна
        """
        self.setGeometry(0, 0, self._width, self._height)
        self.setMaximumSize(self._width, self._height)
        self.setMinimumSize(self._width, self._height)
        self.setWindowTitle('Scrabble')
        self.setWindowIcon(QIcon(self._icon_file_path))
        self.show()

    def init_dict(self):
        """
        Инициализация массива
        """
        self._letters_dict = {'а': 0, 'б': 0, 'в': 0, 'г': 0, 'д': 0, 'е': 0,
                              'ж': 0, 'з': 0, 'и': 0, 'й': 0, 'к': 0, 'л': 0,
                              'м': 0, 'н': 0, 'о': 0, 'п': 0, 'р': 0, 'с': 0,
                              'т': 0, 'у': 0, 'ф': 0, 'х': 0, 'ц': 0, 'ч': 0,
                              'ш': 0, 'щ': 0, 'ъ': 0, 'ы': 0, 'ь': 0, 'э': 0,
                              'ю': 0, 'я': 0, '*': 0}

    def init_buttons(self):
        """
        Инициализация кнопок
        """
        # кнопки с буквами
        self._letters_buttons = []
        for i in range(len(self._letters_dict)):
            if i == len(self._letters_dict) - 1:
                btn_name = '*' + '(0)'
            else:
                btn_name = chr(1072 + i) + '(0)'
            btn = QPushButton(self)
            btn.setText(btn_name)
            btn.clicked.connect(self.letter_btn_pressed)
            self._letters_buttons.append(btn)

        # кнопка сброса счетчика
        drop_button = QPushButton('Сбросить', self)
        drop_button.clicked.connect(self.drop_btn_pressed)
        self._drop_button = drop_button

        # кнопка старта алгоритма
        start_btn = QPushButton(self)
        start_btn.setText('Принять')
        start_btn.clicked.connect(self.start_btn_pressed)

    def init_labels(self):
        """
        Инициализация лейблов
        """
        msg = QLabel(self)
        msg.setText(self._msg_start_caption)
        msg.setStyleSheet('border: 1px solid black;')
        msg.setAlignment(QtCore.Qt.AlignCenter)
        self._msg = msg

    def update_widgets(self):
        """
        Метод обновляет все виджеты
        """
        for i in range(len(self._letters_dict)):
            if i == len(self._letters_dict) - 1:
                btn_name = '*' + '(0)'
            else:
                btn_name = chr(1072 + i) + '(0)'
            self._letters_buttons[i].setText(btn_name)
        self._msg.setText(self._msg_start_caption)

    def draw_widgets(self):
        """
        Метод прорисовывает все виджеты
        """
        for i in range(len(self._letters_dict) + 1):
            if i == len(self._letters_dict):
                self._drop_button.resize(self._cell_size * 2, self._cell_size)
                self._drop_button.move((self._cell_size * i) % self._row_size, (self._cell_size * i) // self._row_size * self._cell_size)
            else:
                self._letters_buttons[i].resize(self._cell_size, self._cell_size)
                self._letters_buttons[i].move((self._cell_size * i) % self._row_size, (self._cell_size * i) // self._row_size * self._cell_size)

        self._msg.resize(self._width, self._cell_size)
        self._msg.move(0, 500)

    # todo: переписать под расчет всех букв на доске
    def letter_btn_pressed(self):
        """
        Метод, вызываемый нажатием на кнопку с буквой или *
        Если в игре еще есть такая буква - увеличивает счетчик этой буквы
        Не более 7 букв в счетчике
        """
        sender = self.sender()
        letter = sender.text()[0]

        if sum(self._letters_dict.values()) < 7:
            print(letter)
            if self._letters_dict[letter] < self._LETTERS_AMOUNT[letter]:
                self._letters_dict[letter] += 1
                sender.setText(letter + '(' + str(self._letters_dict[letter]) + ')')
            else:
                self._msg.setText('В игре больше нет фишек ' + letter)
        else:
            self._msg.setText('Одновременно можно держать только 7 фишек')

    def drop_btn_pressed(self):
        """
        Метод, вызываемый нажатием на кнопку сброса
        Сбрасывает счетчик букв
        """
        self.init_dict()
        self.update_widgets()

    def start_btn_pressed(self):
        """
        Метод, вызываемый нажатием на кнопку старта
        Запускает весь алгоритм
        """

        if sum(self._letters_dict.values()) == 0 and self._board_img is None:
            self._msg.setText('Загрузите изображение и укажите ваши фишки')
        elif sum(self._letters_dict.values()) == 0:
            self._msg.setText('Вы не ввели ни одной фишки')
        elif self._board_img is None:
            self._msg.setText('Вы не загрузили изображение')
        else:
            game_board = None  # распознанная доска
            game_board = [
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'м', ' ', 'т', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'е', ' ', 'о', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', 'п', 'о', 'с', 'е', 'л', 'о', 'к', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', 'а', ' ', 'а', ' ', ' ', ' ', ' ', ' ', 'р', ' ', ' ', ' '],
        [' ', ' ', ' ', 'п', ' ', 'д', 'о', 'м', ' ', 'я', ' ', 'е', ' ', ' ', ' '],
        [' ', ' ', ' ', 'а', ' ', ' ', ' ', 'а', 'з', 'б', 'у', 'к', 'а', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', 'с', 'о', 'м', ' ', 'л', ' ', 'а', ' ', ' ', ' '],
        [' ', ' ', ' ', 'я', 'м', 'а', ' ', 'а', ' ', 'о', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', 'л', ' ', ' ', ' ', 'к', 'и', 'т', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', 'с', 'о', 'л', 'ь', ' ', 'о', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ]
            # убираем пробелы, они нужны были только для удобства ввода
            for test_row in game_board:
                for test_j in range(len(test_row)):
                    if test_row[test_j] == ' ':
                        test_row[test_j] = ''

            hint, value = get_hint(game_board, Counter(self._letters_dict))
            self._msg.setText('Стоимость подсказки с учетом бонусов = '
                              + str(value))
            # todo: отрисовка на доске


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sa = ScrabbleApplication()
    sys.exit(app.exec_())
