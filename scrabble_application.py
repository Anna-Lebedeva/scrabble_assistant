import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon


# author - Pavel
class ScrabbleApplication(QWidget):

    # resolution of the window
    _width = 640
    _height = 960

    # изображение доски (фото)
    _img = None

    # Счетчик букв
    _letters_dict = dict

    _letters_buttons = []  # кнопки с буквами "А"-"Я" + "*"
    _drop_button = None  # кнопка "сбросить счетчик букв"
    _get_hint_button = None  # кнопка "завершить ввод"
    _upload_img_button = None  # кнопка "сделать фото" / "загрузить картинку"

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, self._width, self._height)
        self.setWindowTitle('Scrabble')
        self.setWindowIcon(QIcon('icon.png'))

        self.init_buttons()

        self.show()

    def init_buttons(self):
        cell_size = 50  # размер кнопки с буквой в px
        cells_in_row = (self._width - 20) // cell_size  # кол-во кнопок в линии
        row_size = cell_size * cells_in_row  # длина линии кнопок в px

        for i in range(33):
            btn_name = ""
            if i == 32:
                btn_name = "*"
            else:
                btn_name = chr(1040 + i)

            # кнопки с буквами
            btn = QPushButton(btn_name, self)
            btn.resize(cell_size, cell_size)
            btn.move((cell_size * i) % row_size,
                     (cell_size * i) // row_size * cell_size)

            self._letters_buttons.append(btn)

        # кнопка сброса счетчика
        drop_button_width = 150
        drop_button_height = 60
        drop_button = QPushButton("Сбросить", self)
        drop_button.resize(drop_button_width, drop_button_height)
        drop_button.move((self._width - drop_button_width) // 2, 200)
        self._drop_button = drop_button


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sa = ScrabbleApplication()
    sys.exit(app.exec_())
