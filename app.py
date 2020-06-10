import sys
from collections import Counter

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, \
    QDesktopWidget, QFileDialog

from CV.scan import cut_by_external_contour, cut_by_internal_contour
from CV.exceptions import CutException
from assistant.read_files import read_image, write_image
from assistant.scrabble_assistant import LETTERS_AMOUNT
from assistant.scrabble_assistant import get_used_letters, get_n_hints, \
    is_board_letters_amount_right, delete_alone_letters
from assistant.hint import get_board_with_hints, get_hint_value_coord


# author - Pavel
class ScrabbleApplication(QWidget):
    """
    Application of scrabble-assistant
    Using PyQT5 version 5.14.2
    """

    # может ли приложение корректно работать дальше
    # при status = False не работают никакие кнопки, кроме "загрузить фото"
    # при status = True работает все
    _status = False
    _hints_amount = 5  # сколько подсказок выдавать

    # доска в виде двумерного символьного массива
    _board = None

    # размеры окна и виджетов
    _width = 450  # 450 px
    _height = 805  # 800px
    _chip_size = _width // 9  # размер кнопки с буквой в px
    _row_size = _chip_size * (_width // _chip_size)  # длина линии кнопок в px

    # пути к изображениям
    _blue_chips_folder_path = 'resources/app_images/chips/blue/'
    _red_chips_folder_path = 'resources/app_images/chips/red/'
    _green_chips_folder_path = 'resources/app_images/chips/green/'
    _icon_path = 'resources/app_images/icon.png'  # иконка приложения

    # словари с буквами
    _used_letters = dict()  # словарь с кол-вом букв, которые уже есть на доске
    _chosen_letters = dict()  # словарь с буквами, которые выбрал юзер

    # кнопки
    _letters_buttons = []  # массив кнопок с буквами 'А'-'Я' и '*'
    _letters_on_buttons = []  # массив букв к кнопкам
    _empty_buttons = []
    _chosen_chips_buttons = []  # выбранные буквы. Массив из 7 кнопок
    _drop_button = None  # кнопка 'сбросить счетчик букв'
    _upload_img_button = None  # кнопка 'сделать фото' / 'загрузить картинку'
    _start_button = None  # кнопка по нажатии запускает весь алгоритм

    # labels
    _chosen_chips_labels = None
    _chosen_chips_label_text = 'Выбранные\nфишки:'

    _msg_label = None
    _msg_start = ''
    # _msg_start = 'Загрузите изображение'
    _msg_image_uploaded = 'Выберите ваши фишки'
    _msg_got_hint = 'Подсказки отображены на доске'
    _msg_no_hints = 'Ни одной подсказки не найдено'
    _msg_too_many_letters_error = 'Кол-во некоторых букв на доске ' \
                                  'превышает допустимое игрой значение'
    _msg_max_chips_error = 'Одновременно можно держать только 7 фишек'
    _msg_max_chip_error = 'В игре больше нет фишек '
    _msg_no_img_no_chips_error = 'Загрузите изображение и выберите ваши фишки'
    _msg_no_chips_error = 'Вы не выбрали ни одной фишки'
    _msg_no_img_error = 'Вы не загрузили изображение'
    _msg_scan_error = 'Ошибка: доска не распознана'

    _img_label = None  # label для изображения доски
    _board_img = None  # обрезанное изображение доски

    _hints_labels = []  # фишки подсказок, отображаемые на экране
    _got_hints = False  # получена ли подсказка

    def __init__(self):
        """
        Инициализация приложения
        """
        super().__init__(flags=Qt.Widget)
        self.init_buttons()
        self.init_labels()
        self.init_ui()
        self.draw_widgets()

    def init_ui(self):
        """
        Инициализация интерфейса
        """
        size = QDesktopWidget().screenGeometry(-1)
        width = size.width()
        height = size.height()
        self.setGeometry((width - self._width) // 2,
                         (height - self._height) // 2,
                         self._width, self._height)
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
        start_btn.setText('Готово')
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

        # пустые кнопки в конце клавиатуры
        for i in range(3):
            btn = QPushButton(self)
            self._empty_buttons.append(btn)

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
            label.setAlignment(Qt.AlignCenter)
            label.setText('')
            label.setStyleSheet('font-size: 22px;')
            self._hints_labels.append(label)

        # msg label
        label = QLabel(self)
        label.setText(self._msg_start)
        label.setAlignment(Qt.AlignCenter)  # выровнять текст по центру
        self._msg_label = label

    def image_uploaded(self):
        """
        Проверка загруженного изображения и его показ на экране
        """

        fd = QFileDialog()  # диалоговое окно для выбора файла
        option = fd.Options()  # стандартный выбор файла
        img_path = fd.getOpenFileName(self, caption="Выбор фотографии",
                                      filter="Image files (*.jpg)",
                                      options=option)[0]

        # если изображение так и не было выбрано - выходим из функции
        if not img_path:
            return

        # обработка изображения
        try:
            img = read_image(img_path)  # считывание
            img = cut_by_external_contour(img)  # обрезка по внешнему контуру
            img = cut_by_internal_contour(img)  # обрезка по внутреннему контуру
        except (CutException, AttributeError):
            self._img_label.setPixmap(QPixmap())  # убираем изображение доски
            self._msg_label.setText(self._msg_scan_error)  # error msg
            # todo: блокировка приложения
            # todo: disable на все кнопки, кроме загрузки изображения
            # fixme баг с вызовом clear_widgets()
            # self.clear_widgets()
            return

        # распознавание доски с помощью натренированной модели
        # board = []  # распознанная доска в виде двумерного символьного массива
        # try:
        #     pass
        #     # todo: здесь будет распознавание
        # # todo: подумать над исключениями
        # except (Exception):
        #     self._msg_label.setText(self._msg_scan_error)
        #     return

        board = [
            ['', 'я', '', '', '', '', '', '', '', '', '', '', '', '', ''],
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
            ['', 'р', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', '', '', '', '', '', 'у', ''],
        ]

        # удаляем помехи из таблицы
        # если букву не окружают другие буквы хотя бы с одной стороны
        # удаляем ее
        board = delete_alone_letters(board)
        self._board = board

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

            self._status = True  # запускаем приложение
            self._msg_label.setText(self._msg_image_uploaded)
            self.clear_widgets()
        else:
            # если превышено кол-во хоть одной из букв
            self._msg_label.setText(self._msg_too_many_letters_error)
            self._status = False  # блокируем приложение

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

        for label in self._hints_labels:
            label.setPixmap(QPixmap())
            label.setText('')

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
        for label in self._hints_labels:
            label.resize(label_size - 1, label_size - 1)
            x_pos = index % self._width
            y_pos = index // self._width * label_size
            index += label_size
            label.move(x_pos + 1, y_pos + current_height + 1)
        current_height += height

        # прорисовка msg label
        height = self._chip_size - 5
        self._msg_label.resize(self._width, height)
        self._msg_label.move(0, current_height)
        current_height += height

        height = self._chip_size
        # прорисовка выбранных букв
        for i in range(len(self._chosen_chips_buttons)):
            self._chosen_chips_buttons[i].resize(self._chip_size,
                                                 self._chip_size)
            self._chosen_chips_buttons[i].move(i * self._chip_size,
                                               current_height)

        # прорисовка кнопки "сброс"
        self._drop_button.resize(self._chip_size * 2, self._chip_size)
        self._drop_button.move(7 * self._chip_size, current_height)

        current_height += height

        # разрыв в 5 пикселей
        current_height += 5

        # прорисовка кнопок с буквами для выбора
        index = 0  # суммарная длина всех прошлых кнопок
        for btn in self._letters_buttons:
            btn.resize(self._chip_size, self._chip_size)
            x_pos = index % self._row_size
            y_pos = index // self._row_size * self._chip_size
            index += self._chip_size
            btn.move(x_pos, y_pos + current_height)

        # три кнопки в конце клавиатуры
        for btn in self._empty_buttons:
            btn.resize(self._chip_size, self._chip_size)
            x_pos = index % self._row_size
            y_pos = index // self._row_size * self._chip_size
            index += self._chip_size
            btn.move(x_pos, y_pos + current_height)

        current_height += 4 * height

        # разрыв в 5 пикселей
        current_height += 5

        # прорисовка кнопки для выбора фото
        height = self._chip_size
        self._upload_img_button.resize(self._width // 2, height)
        self._upload_img_button.move(0, current_height)

        # прорисовка кнопки старта
        self._start_button.resize(self._width // 2, height)
        self._start_button.move(self._width // 2, current_height)
        current_height += height

    def letter_btn_pressed(self, letter: str = None):
        """
        Добавление фишки к выбранным фишкам, если это возможно
        """
        # кнопка не работает, если приложение заблокировано
        if not self._status:
            return

        # если кнопка была активирована нажатием на нее, а не клавиатурой
        if not letter:
            # определяем какая именно кнопка вызвала функцию
            # и записываем ее букву
            for i in range(len(self._letters_buttons)):
                if self._letters_buttons[i] == self.sender():
                    letter = self._letters_on_buttons[i]
                    break

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

    def keyPressEvent(self, event: QKeyEvent):
        """
        Обработка нажатий на кнопки клавиатуры
        """

        key = event.key()  # ключ нажатой кнопки
        text = event.text().lower()  # текст нажатой кнопки
        if text == 'ё':
            text = 'е'

        # выход из программы по нажатию Escape
        if key == Qt.Key_Escape:
            self.close()
        # запуск алгоритма по нажатию Enter
        elif key == Qt.Key_Return:
            self.start_btn_pressed()
        # сброс по нажатию Backspace
        elif key == Qt.Key_Backspace:
            self.drop_btn_pressed()
        # если нажатая кнопка - один символ
        elif len(text) == 1:
            # если это латинская буква в нижнем регистре
            if 1072 <= ord(text) <= 1103:
                # производим нажатие нужной кнопки
                self.letter_btn_pressed(text)
            # отдельная обработка звездочки
            elif text == '*':
                self.letter_btn_pressed('*')

    def drop_btn_pressed(self):
        """
        Сброс виджетов
        """

        # кнопка не работает, если приложение заблокировано
        if not self._status:
            return

        self.clear_widgets()

    def start_btn_pressed(self):
        """
        Запуск алгоритма
        """

        # кнопка не работает, если приложение заблокировано
        if not self._status:
            return

        # очистка подсказки, если запуск идет не в первый раз
        if self._got_hints:
            self.clear_hint()

        if sum(self._chosen_letters.values()) == 0 and self._board_img is None:
            self._msg_label.setText(self._msg_no_img_no_chips_error)
        elif sum(self._chosen_letters.values()) == 0:
            self._msg_label.setText(self._msg_no_chips_error)
        elif self._board_img is None:
            self._msg_label.setText(self._msg_no_img_error)
        else:
            # запуск алгоритма
            hints, values = get_n_hints(self._board,
                                        Counter(self._chosen_letters),
                                        self._hints_amount)
            if len(hints) != 0:
                # отрисовка подсказки на экране
                self.draw_hint(hints, values)
                # выводим стоимость подсказки
                self._msg_label.setText(self._msg_got_hint)
                self._got_hints = True
            else:
                self._msg_label.setText(self._msg_no_hints)

    def draw_hint(self, hints: [[[str]]], values: [int]):
        """
        Отрисовка подсказок на экране
        """

        # объединение доски с подсказками и их ценностями
        combined_board = get_board_with_hints(self._board, hints)
        color_index = 0  # индекс цвета для вывода подсказок

        for i in range(len(hints)):
            # идем по доске подсказок
            for y in range(len(hints[i])):
                for x in range(len(hints[i][y])):
                    # отрисовываем букву если:
                    # на подсказке эта буква есть
                    # а на доске этой буквы еще нет
                    if hints[i][y][x] != '' and self._board[y][x] == '':
                        # поиск индекса буквы в алфавите
                        # отдельная обработка звездочки
                        if hints[i][y][x] == '*':
                            chip_index = 32
                        else:
                            chip_index = ord(hints[i][y][x]) - 1072

                        # размер одной фишки на изображении
                        hint_size = self._width // 15  # 30px
                        # находим нужный label в массиве
                        hint_label = self._hints_labels[y * 15 + x]
                        # выбор файла изображения
                        img_folder = self._green_chips_folder_path
                        img_filename = 'letter' + str(chip_index + 1) + '.jpg'
                        pix = QPixmap(img_folder + img_filename)
                        # масштабирование изображения под фишку
                        pix = pix.scaledToWidth(hint_size)
                        pix = pix.scaledToHeight(hint_size)
                        # установка изображения
                        hint_label.setPixmap(pix)
            # определяем слово как гориз. или верт.
            # по приоритетам находим лучшую точку
            # рисуем

            y, x = get_hint_value_coord(hints[i], combined_board)
            combined_board[y][x] = '$'
            label = self._hints_labels[y * 15 + x]
            label.setText(str(values[i]))
            label.setStyleSheet('font-size: 22px; color: red;')

            color_index += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scrabble = ScrabbleApplication()
    sys.exit(app.exec_())
