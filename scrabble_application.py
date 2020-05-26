from collections import Counter

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QPixmap
import sys


# author - Pavel
class ScrabbleApplication(QWidget):

    import scrabble_assistant as sa

    # может ли приложение корректно работать дальше
    # при status = False не работают никакие кнопки, кроме "загрузить фото"
    # при status = True работает все
    status = True

    # доска
    _board = [
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', 'м', '', 'т', '', '', '', '', ''],
        ['', '', '', '', '', '', '', 'е', '', 'о', '', '', '', '', ''],
        ['', '', '', 'п', 'о', 'с', 'е', 'л', 'о', 'к', '', '', '', '', ''],
        ['', '', '', 'а', '', 'а', '', '', '', '', '', 'р', '', '', ''],
        ['', '', '', 'п', '', 'д', 'о', 'м', '', 'я', '', 'е', '', '', ''],
        ['', '', '', 'а', '', '', '', 'а', 'з', 'б', 'у', 'к', 'а', '', ''],
        ['', '', '', '', '', 'с', 'о', 'м', '', 'л', '', 'а', '', '', ''],
        ['', '', '', 'я', 'м', 'а', '', 'а', '', 'о', '', '', '', '', ''],
        ['', '', '', '', '', 'л', '', '', '', 'к', 'и', 'т', '', '', ''],
        ['', '', '', '', 'с', 'о', 'л', 'ь', '', 'о', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    ]

    # resolution of the window
    _width = 420
    _height = 800

    # изображения
    #
    _board_img = 0  # изображение доски (фото)
    _icon_file_path = 'app_images/icon.png'
    _background_file_path = 'app_images/app_background.jpg'  # фон

    # словари с буквами
    _letters_used = dict()   # словарь с кол-вом букв, которые уже есть на доске
    _letters_dict = dict()  # словарь с буквами, которые выбрал юзер

    # кнопки
    _letters_buttons = []  # массив кнопок с буквами 'А'-'Я' и '*'
    _letters_on_buttons = []  # массив букв к кнопкам
    _chosen_chips = []  # выбранные буквы. Массив из 7 кнопок
    _drop_button = None  # кнопка 'сбросить счетчик букв'
    _get_hint_button = None  # кнопка 'завершить ввод'
    _upload_img_button = None  # кнопка 'сделать фото' / 'загрузить картинку'
    _start_button = None  # кнопка по нажатии запускает весь алгоритм

    # labels
    _msg = ""
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

        self.image_uploaded()

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
        self._letters_on_buttons = []
        for i in range(len(self._letters_dict)):
            if i == len(self._letters_dict) - 1:
                letter_on_button = '*'
            else:
                letter_on_button = chr(1072 + i)
            btn = QPushButton(self)

            image_path = 'app_images/chips/blue/letter' + str(i + 1) + '.jpg'
            btn.setIcon(QIcon(image_path))
            btn.setIconSize(QSize(self._cell_size, self._cell_size))

            self._letters_on_buttons.append(letter_on_button)
            btn.clicked.connect(self.letter_btn_pressed)
            self._letters_buttons.append(btn)

        # кнопка сброса счетчика
        drop_button = QPushButton('Сбросить', self)
        drop_button.clicked.connect(self.drop_btn_pressed)
        self._drop_button = drop_button

        # кнопки выбранных букв
        self._chosen_chips = []
        for i in range(7):
            btn = QPushButton(self)
            # btn.setIcon(QIcon('app_images/chips/blue/letter1.jpg'))
            # btn.setIconSize(QSize(self._cell_size, self._cell_size))
            self._chosen_chips.append(btn)

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

    def image_uploaded(self):
        """
        Проверка загруженного изображения и его показ на экране
        """
        # если кол-во всех букв на доске не больше допустимого
        if self.sa.is_board_letters_amount_right(self._board):
            # записываем кол-во всех букв на доске
            self._letters_used = self.sa.get_used_letters_counter(self._board)
            self.status = True
        else:
            # если превышено кол-во хоть одной из букв
            self._msg.setText('Кол-во некоторых букв на доске '
                              'превышает допустимое игрой значение')
            self.status = False
            return
        # todo: загрузка и показ изображения

    def update_widgets(self):
        """
        Метод обновляет все виджеты
        """
        self._msg.setText(self._msg_start_caption)

        for i in range(7):
            btn = self._chosen_chips[i]
            btn.setIcon(QIcon())
            self._chosen_chips[i] = btn

    def draw_widgets(self):
        """
        Метод прорисовывает все виджеты
        """
        # прорисовка кнопок с буквами для выбора
        for i in range(len(self._letters_dict) + 1):
            if i == len(self._letters_dict):
                # прорисовка кнопки "сброс"
                self._drop_button.resize(self._cell_size * 2, self._cell_size)
                self._drop_button.move((self._cell_size * i) % self._row_size, (self._cell_size * i) // self._row_size * self._cell_size)
            else:
                self._letters_buttons[i].resize(self._cell_size, self._cell_size)
                self._letters_buttons[i].move((self._cell_size * i) % self._row_size, (self._cell_size * i) // self._row_size * self._cell_size)

        # msg label
        self._msg.resize(self._width, self._cell_size)
        self._msg.move(0, 500)

        # chosen letters btn
        for i in range(len(self._chosen_chips)):
            self._chosen_chips[i].resize(self._cell_size, self._cell_size)
            self._chosen_chips[i].move(i * self._cell_size, 400)

    # todo: переписать под расчет всех букв на доске
    def letter_btn_pressed(self):
        """
        Метод, вызываемый нажатием на кнопку с буквой или *
        Если в игре еще есть такая буква - увеличивает счетчик этой буквы
        Не более 7 букв в счетчике
        """
        if not self.status:
            return

        letter = ''
        for i in range(len(self._letters_buttons)):
            if self._letters_buttons[i] == self.sender():
                letter = self._letters_on_buttons[i]

        # проверка на наличие 7 фишек
        if sum(self._letters_dict.values()) < 7:
            # проверка на наличие в игре достаточного количества фишек
            if self._letters_dict[letter] + self._letters_used[letter] < \
                    self.sa.LETTERS_AMOUNT[letter]:

                chosen_chip_index = ord(letter) - 1072
                btn = self._chosen_chips[sum(self._letters_dict.values())]
                image_path = 'app_images/chips/blue/letter' + \
                             str(chosen_chip_index + 1) + '.jpg'
                btn.setIcon(QIcon(image_path))
                btn.setIconSize(QSize(self._cell_size, self._cell_size))
                self._chosen_chips[sum(self._letters_dict.values())] = btn

                self._letters_dict[letter] += 1

            else:
                self._msg.setText('В игре больше нет фишек ' + letter)
        else:
            self._msg.setText('Одновременно можно держать только 7 фишек')

    def drop_btn_pressed(self):
        """
        Метод, вызываемый нажатием на кнопку сброса
        Сбрасывает счетчик букв
        """
        if not self.status:
            return

        self.init_dict()
        self.update_widgets()

    def start_btn_pressed(self):
        """
        Метод, вызываемый нажатием на кнопку старта
        Запускает весь алгоритм
        """
        if not self.status:
            return

        if sum(self._letters_dict.values()) == 0 and self._board_img is None:
            self._msg.setText('Загрузите изображение и укажите ваши фишки')
        elif sum(self._letters_dict.values()) == 0:
            self._msg.setText('Вы не ввели ни одной фишки')
        elif self._board_img is None:
            self._msg.setText('Вы не загрузили изображение')
        else:
            # убираем пробелы, они нужны были только для удобства ввода
            for test_row in self._board:
                for test_j in range(len(test_row)):
                    if test_row[test_j] == ' ':
                        test_row[test_j] = ''

            hint, value = self.sa.get_hint(self._board, Counter(self._letters_dict))
            self._msg.setText('Стоимость подсказки с учетом бонусов = '
                              + str(value))
            # todo: отрисовка на доске


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sa = ScrabbleApplication()
    sys.exit(app.exec_())
