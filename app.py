import sys
from collections import Counter

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel

from CV.scan import cut_by_external_contour, cut_by_internal_contour
from assistant.read_files import read_image, write_image
from assistant.scrabble_assistant import LETTERS_AMOUNT
from assistant.scrabble_assistant import get_used_letters, get_hint, \
    is_board_letters_amount_right


# author - Pavel
class ScrabbleApplication(QWidget):
    """
    Application of scrabble-assistant
    Using PyQT5 version 5.14.2
    """

    # может ли приложение корректно работать дальше
    # при status = False не работают никакие кнопки, кроме "загрузить фото"
    # при status = True работает все
    status = False

    # доска в виде двумерного символьного массива
    _board = None

    # размеры окна и виджетов
    _width = 450  # 450 px
    _height = int(_width * 1.7777777)  # 800px
    _chip_size = _width // 9  # размер кнопки с буквой в px
    _row_size = _chip_size * (_width // _chip_size)  # длина линии кнопок в px

    # пути к изображениям
    _blue_chips_folder_path = 'resources/app_images/chips/blue/'
    _red_chips_folder_path = 'resources/app_images/chips/red/'
    _green_chips_folder_path = 'resources/app_images/chips/green/'
    _icon_path = 'resources/app_images/icon.png'  # иконка приложения
    _background_path = 'resources/app_images/background.jpg'  # фон

    # словари с буквами
    _used_letters = dict()  # словарь с кол-вом букв, которые уже есть на доске
    _chosen_letters = dict()  # словарь с буквами, которые выбрал юзер

    # кнопки
    _letters_buttons = []  # массив кнопок с буквами 'А'-'Я' и '*'
    _letters_on_buttons = []  # массив букв к кнопкам
    _chosen_chips_buttons = []  # выбранные буквы. Массив из 7 кнопок
    _drop_button = None  # кнопка 'сбросить счетчик букв'
    _upload_img_button = None  # кнопка 'сделать фото' / 'загрузить картинку'
    _start_button = None  # кнопка по нажатии запускает весь алгоритм

    # labels
    _chosen_chips_labels = None
    _chosen_chips_label_text = 'Выбранные\nфишки:'

    _msg_label = None
    _msg_start = 'Загрузите фото'
    _msg_image_uploaded = 'Выберите ваши фишки, кликая по ним'
    _msg_hint_value = 'Ценность подсказки = '
    _msg_too_many_letters_error = 'Кол-во некоторых букв на доске ' \
                                  'превышает допустимое игрой значение'
    _msg_max_chips_error = 'Одновременно можно держать только 7 фишек'
    _msg_max_chip_error = 'В игре больше нет фишек '
    _msg_no_img_no_chips_error = 'Загрузите изображение и укажите ваши фишки'
    _msg_no_chips_error = 'Вы не ввели ни одной фишки'
    _msg_no_img_error = 'Вы не загрузили изображение'

    _img_label = None  # label для изображения доски
    _board_img = None  # обрезанное изображение доски

    _hint_labels = []  # фишки подсказок, отображаемые на экране
    _is_hint_showing = False  # получена ли подсказка

    def __init__(self):
        """
        Инициализация приложения
        """
        super().__init__()

        self.init_buttons()
        self.init_labels()
        self.init_ui()
        self.draw_widgets()

    def init_ui(self):
        """
        Инициализация интерфейса
        """
        self.setGeometry(0, 0, self._width, self._height)
        self.setMaximumSize(self._width, self._height)
        self.setMinimumSize(self._width, self._height)
        self.setWindowTitle('Scrabble')
        self.setWindowIcon(QIcon(self._icon_path))
        self.show()

    def init_dicts(self):
        """
        Инициализация словарей
        """

        # словарь с выбранными буквами
        self._chosen_letters = {'а': 0, 'б': 0, 'в': 0, 'г': 0, 'д': 0, 'е': 0,
                                'ж': 0, 'з': 0, 'и': 0, 'й': 0, 'к': 0, 'л': 0,
                                'м': 0, 'н': 0, 'о': 0, 'п': 0, 'р': 0, 'с': 0,
                                'т': 0, 'у': 0, 'ф': 0, 'х': 0, 'ц': 0, 'ч': 0,
                                'ш': 0, 'щ': 0, 'ъ': 0, 'ы': 0, 'ь': 0, 'э': 0,
                                'ю': 0, 'я': 0, '*': 0}
        # словарь с буквами, которые уже есть на доске
        self._used_letters = get_used_letters(self._board)

    def init_buttons(self):
        """
        Инициализация кнопок
        """

        # кнопка загрузки изображения
        btn = QPushButton(self)
        btn.setText('Загрузить изображение')
        btn.clicked.connect(self.image_uploaded)
        self._upload_img_button = btn

        # кнопка старта алгоритма
        start_btn = QPushButton(self)
        start_btn.setText('Принять')
        start_btn.clicked.connect(self.start_btn_pressed)
        self._start_button = start_btn

        # кнопки выбранных фишек
        self._chosen_chips_buttons = []
        for i in range(7):
            btn = QPushButton(self)
            btn.setIconSize(QSize(self._chip_size, self._chip_size))
            self._chosen_chips_buttons.append(btn)

        # кнопки с фишками-буквами
        self._letters_buttons = []
        self._letters_on_buttons = []
        for i in range(33):
            if i == 32:
                letter_on_button = '*'
            else:
                letter_on_button = chr(1072 + i)
            self._letters_on_buttons.append(letter_on_button)
            btn = QPushButton(self)
            image_path = self._blue_chips_folder_path + str(i + 1) + '.jpg'
            btn.setIcon(QIcon(image_path))
            btn.setIconSize(QSize(self._chip_size, self._chip_size))
            btn.clicked.connect(self.letter_btn_pressed)
            self._letters_buttons.append(btn)

        # кнопка сброса счетчика
        drop_button = QPushButton('Сбросить', self)
        drop_button.clicked.connect(self.drop_btn_pressed)
        self._drop_button = drop_button

    def init_labels(self):
        """
        Инициализация labels
        """

        # img label
        label = QLabel(self)
        self._img_label = label

        # hint labels
        for i in range(225):
            label = QLabel(self)
            self._hint_labels.append(label)

        # chosen chips label
        label = QLabel(self)
        label.setText(self._chosen_chips_label_text)
        label.setAlignment(Qt.AlignCenter)
        self._chosen_chips_labels = label

        # msg label
        label = QLabel(self)
        label.setText(self._msg_start)
        label.setAlignment(Qt.AlignCenter)  # выровнять текст по центру
        self._msg_label = label

    def image_uploaded(self):
        """
        Проверка загруженного изображения и его показ на экране
        """

        # menu = self.menuBar()
        # file_menu = menu.addMenu('File')
        #
        # dlg = QFileDialog(self)
        # open_action = QAction('Open image', self)
        # open_action.triggered.connect(self.open_image)
        # file_menu.addAction(open_action)

        # todo: загрузка юзером
        # обработка изображения
        img = read_image('resources/app_images/test.jpg')
        # обрезка по внешнему контуру
        img = cut_by_external_contour(img)
        # обрезка по внутреннему контуру
        img = cut_by_internal_contour(img)

        # todo: здесь будет распознавание нейросетью

        self._board = [
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
        # записываем изображение
        write_image(img, 'resources/app_images/user_image.jpg')

        # считываем изображение
        img = QPixmap('resources/app_images/user_image.jpg')
        # уменьшаем до размеров экрана
        img = img.scaledToHeight(self._width)
        img = img.scaledToWidth(self._width)

        # сохраняем
        self._board_img = img
        self._img_label.setPixmap(self._board_img)

        # если кол-во всех букв на доске не больше допустимого
        if is_board_letters_amount_right(self._board):

            self.status = True  # запускаем приложение
            self.init_dicts()  # инициализируем словари
            self._msg_label.setText(self._msg_image_uploaded)
            self.clear_widgets()
        else:
            # если превышено кол-во хоть одной из букв
            self._msg_label.setText(self._msg_too_many_letters_error)
            self.status = False  # блокируем приложение

    def clear_widgets(self):
        """
        Обновление всех виджетов
        """

        # повторная инициализация словарей
        self.init_dicts()
        # обновляем кнопки
        self.update_buttons()
        # сбрасываем msg
        self._msg_label.setText(self._msg_image_uploaded)

        # сбрасываем все выбранные фишки
        for i in range(7):
            btn = self._chosen_chips_buttons[i]
            btn.setIcon(QIcon())
            self._chosen_chips_buttons[i] = btn

        # очистка подсказки
        self.clear_hint()

    def clear_hint(self):
        """
        Удаление подсказки с экрана
        """

        for label in self._hint_labels:
            label.setPixmap(QPixmap())

    def update_buttons(self):
        """
        Обновляет все кнопки-фишки, при необходимости меняя их цвет
        """
        # идем по всем кнопкам с буквами
        for i in range(len(self._letters_buttons)):
            # получаем букву, расположенную на кнопке
            letter = self._letters_on_buttons[i]

            # если фишку можно взять, то она синяя, если нельзя - красная
            # далее проверяем. можно ли взять еще одну фишку
            # проверка на наличие 7 фишек
            if sum(self._chosen_letters.values()) < 7:
                # проверка на наличие в игре достаточного количества таких фишек
                if self._chosen_letters[letter] + self._used_letters[letter] < \
                        LETTERS_AMOUNT[letter]:
                    # путь к папке с изображениями фишек
                    chips_img_path = self._blue_chips_folder_path
                    chips_img_path += 'letter' + str(i + 1) + '.jpg'
                else:
                    chips_img_path = self._red_chips_folder_path
                    chips_img_path += 'letter' + str(i + 1) + '.jpg'
            else:
                chips_img_path = self._red_chips_folder_path
                chips_img_path += 'letter' + str(i + 1) + '.jpg'

            # получаем путь к файлу изображения кнопки
            image_path = chips_img_path  # путь к файлу
            # устанавливаем правильную иконку на кнопку
            self._letters_buttons[i].setIcon(QIcon(image_path))

    def draw_widgets(self):
        """
        Прорисовка всех виджетов на экране
        """

        # текущая глубина для расположения виджетов друг за другом
        current_height = 0

        # прорисовка img label
        height = self._width
        self._img_label.resize(self._width, height)
        self._img_label.move(0, current_height)

        index = 0  # суммарная длина всех прошлых labels
        label_size = self._width // 15
        for label in self._hint_labels:
            label.resize(label_size - 1, label_size - 1)
            x_pos = index % self._width
            y_pos = index // self._width * label_size
            index += label_size
            label.move(x_pos + 1, y_pos + current_height + 1)
        current_height += height

        # прорисовка кнопки для выбора фото
        height = self._chip_size
        self._upload_img_button.resize(self._width // 2, height)
        self._upload_img_button.move(0, current_height)

        # прорисовка кнопки старта
        self._start_button.resize(self._width // 2, height)
        self._start_button.move(self._width // 2, current_height)
        current_height += height

        # прорисовка chosen chips label
        height = self._chip_size
        self._chosen_chips_labels.resize(self._chip_size * 2, self._chip_size)
        self._chosen_chips_labels.move(0, current_height)

        # прорисовка выбранных букв
        for i in range(len(self._chosen_chips_buttons)):
            self._chosen_chips_buttons[i].resize(self._chip_size,
                                                 self._chip_size)
            self._chosen_chips_buttons[i].move((i + 2) * self._chip_size,
                                               current_height)
        current_height += height

        # прорисовка msg label
        height = self._chip_size
        self._msg_label.resize(self._width, height)
        self._msg_label.move(0, current_height)
        current_height += height

        # прорисовка кнопок с буквами для выбора
        index = 0  # суммарная длина всех прошлых кнопок
        for btn in self._letters_buttons:
            btn.resize(self._chip_size, self._chip_size)
            x_pos = index % self._row_size
            y_pos = index // self._row_size * self._chip_size
            index += self._chip_size
            btn.move(x_pos, y_pos + current_height)

        # прорисовка кнопки "сброс"
        self._drop_button.resize(self._chip_size * 3, self._chip_size)
        x_pos = index % self._row_size
        y_pos = index // self._row_size * self._chip_size
        self._drop_button.move(x_pos, y_pos + current_height)

    def letter_btn_pressed(self):
        """
        Добавление фишки к выбранным фишкам, если эт возможно
        """
        # кнопка не работает, если приложение заблокировано
        if not self.status:
            return

        # определяем какая именно кнопка вызвала функцию
        # и записываем ее букву
        letter = ''
        for i in range(len(self._letters_buttons)):
            if self._letters_buttons[i] == self.sender():
                letter = self._letters_on_buttons[i]

        # проверка на наличие 7 фишек
        if sum(self._chosen_letters.values()) < 7:
            # проверка на наличие в игре достаточного количества фишек
            if self._chosen_letters[letter] + self._used_letters[letter] < \
                    LETTERS_AMOUNT[letter]:
                # определяем букву кнопки
                # отдельный случай со звездочкой
                if letter == '*':
                    chosen_chip_index = 32
                else:
                    chosen_chip_index = ord(letter) - 1072

                # находим фишку в выбранных фишках, которую будем отображать
                chosen_chip_position = sum(self._chosen_letters.values())
                btn = self._chosen_chips_buttons[chosen_chip_position]

                # путь к файлу-картинке
                image_filename = 'letter' + str(chosen_chip_index + 1) + '.jpg'
                image_path = self._blue_chips_folder_path + image_filename

                btn.setIcon(QIcon(image_path))

                # добавляем фишку в словарь выбранных фишек
                self._chosen_letters[letter] += 1
                # обновляем цвет фишек
                self.update_buttons()
            else:
                # если кол-во данны букв уже закончилось - выводим сообщение
                self._msg_label.setText(self._msg_max_chip_error
                                        + letter.upper())
        else:
            # если 7 фишек уже выбрано - выводим об этом сообщение
            self._msg_label.setText(self._msg_max_chips_error)

    def drop_btn_pressed(self):
        """
        Сброс виджетов
        """

        # кнопка не работает, если приложение заблокировано
        if not self.status:
            return

        self.clear_widgets()

    def start_btn_pressed(self):
        """
        Запуск алгоритма
        """

        # кнопка не работает, если приложение заблокировано
        if not self.status:
            return

        # очистка подсказки, если запуск идет не в первый раз
        if self._is_hint_showing:
            self.clear_hint()

        if sum(self._chosen_letters.values()) == 0 and self._board_img is None:
            self._msg_label.setText(self._msg_no_img_no_chips_error)
        elif sum(self._chosen_letters.values()) == 0:
            self._msg_label.setText(self._msg_no_chips_error)
        elif self._board_img is None:
            self._msg_label.setText(self._msg_no_img_error)
        else:
            # запуск алгоритма
            hint, value = get_hint(self._board, Counter(self._chosen_letters))
            # отрисовка подсказки на экране
            self.draw_hint(hint)
            # выводим стоимость подсказки
            self._msg_label.setText(self._msg_hint_value + str(value))
            self._is_hint_showing = True

    def draw_hint(self, hint):
        """
        Отрисовка подсказки на экране
        """

        # идем по доске подсказок
        for y in range(len(hint)):
            for x in range(len(hint[y])):
                # отрисовываем букву если:
                # на подсказке эта буква есть
                # а на доске этой буквы еще нет
                if hint[y][x] != '' and self._board[y][x] == '':
                    # поиск индекса буквы в алфавите
                    # отдельная обработка звездочки
                    if hint[y][x] == '*':
                        chip_index = 32
                    else:
                        chip_index = ord(hint[y][x]) - 1072

                    # размер одной фишки на изображении
                    hint_size = self._width // 15  # 30px
                    # находим нужный label в массиве
                    hint_label = self._hint_labels[y * 15 + x]
                    # выбор файла изображения
                    img_filename = 'letter' + str(chip_index + 1) + '.jpg'
                    pix = QPixmap(self._green_chips_folder_path + img_filename)
                    # масштабирование изображения под фишку
                    pix = pix.scaledToWidth(hint_size)
                    pix = pix.scaledToHeight(hint_size)
                    # установка изображения
                    hint_label.setPixmap(pix)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scrabble = ScrabbleApplication()
    sys.exit(app.exec_())
