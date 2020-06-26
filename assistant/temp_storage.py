import re
from pathlib import Path

from assistant.scrabble_assistant import LETTERS_VALUES


# author - Matvey
# fixme: не дописано
def get_regex_patterns(sharped_row: [str]) -> ([re.Pattern], [[str]]):
    """
    Получает строку, возвращает паттерны, соответствующие этой строке,
    для поиска подходящих слов в словаре по этому паттерну.
    :param sharped_row: размеченный '#' ряд
    :return: шаблоны, по которому можно найти подходящие слова и список для
    каждого шаблона, где находятся буквы из этого шаблона
    """

    prepared_row = []
    patterns = []
    letters = []
    letters_in_patterns = []
    # test_row = ['', '', '', 'а', '#', 'а', '#',
    # '#', '#', '#', '', 'р', '', '', '']

    for cell in range(len(sharped_row)):
        if sharped_row[cell]:  # Если в клетке есть символ
            prepared_row.append(sharped_row[cell])
        else:  # Если клетка пустая
            prepared_row.append('')
            # fixme: переписать?

    prepared_row = ''.join(prepared_row).split('#')
    # Соединяем в строку и нарезаем на подстроки по '#'

    for i in range(len(prepared_row)):
        if len(prepared_row[i]) > 1:
            # отбираем подстроки длинее 1 символа
            patterns.append(prepared_row[i])

    for pattern in patterns:
        for i in pattern:
            if i.isalpha():
                letters.append(i)
        letters_in_patterns.append(letters)
        letters = []

    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace('', '[а-я]?')
    # В пустое место можно вписать любую букву букву а-я или не писать ничего
    # todo: Можно переписать регулярку c помощью одних фигурных скобок

    for i in range(len(patterns)):
        patterns[i] = '^(' + patterns[i] + ')$'
    # Чтобы регулярка не хватала слова,
    # которые удовлетворяют, но выходят за рамки.

    for i in range(len(patterns)):
        patterns[i] = re.compile(patterns[i])
    # Компилируем каждый паттерн в регулярное выражение
    # Upd. компиляция не понадобится. Но пока не удалять

    return patterns, letters_in_patterns


# author: Matvey
# todo: удалить или все же пригодится?
def calculate_letters_value(word: str) -> int:
    """
    Считает ценность слова, без учета бонусов.
    :param word: слово, ценность которого нужно посчитать
    :return: ценность слова, без учета бонусов
    """

    return sum([LETTERS_VALUES[letter] for letter in word])


# author: Matvey
# fixme: у нас изменились пути, переписать
# todo: может вернуть не имя файла, а путь к нему?
def get_smallest_sub_dict(letters_in_pattern: [str]) -> str:
    """
    Выбирает из списка букв самую редкую
    и возвращает название подсловаря с этой буквой.
    :param letters_in_pattern: список букв, которые есть в паттерне
    :return: имя наименьшего словаря
    """

    min_sub_dict_name = ''  # Название наименьшего словаря
    min_sub_dict_size = Path(Path.cwd() / 'dictionary15.txt').stat().st_size

    # Считываем название полного словаря
    for i in letters_in_pattern:  # Идем по буквам
        sub_dict_letter = str('letter' + str(ord(i) - 1071) + '.txt')
        # Получаем название подсловаря

        sub_dict_size = Path(Path.cwd() / 'sub-dictionaries' /
                             sub_dict_letter).stat().st_size
        # Получаем размер подсловаря

        # Если размер подсловаря меньше минимального
        if sub_dict_size < min_sub_dict_size:
            min_sub_dict_name = sub_dict_letter
            min_sub_dict_size = sub_dict_size

    return min_sub_dict_name


# author - Matvey
def is_word_fit_to_pattern(word: str, pattern: re.Pattern) -> bool:
    """
    Проверяет - подходит ли слово в паттерн.
    :param word: слово
    :param pattern: паттерн
    :return:
    """

    # todo: вернуть индексы
    return bool(pattern.search(word))


# Автор: Матвей
def arrange_long_word_to_empty_board(word: str) -> int:
    """Располагает слово, длиной от 5 до 7 на стартовой доске наилучшим образом,
    с учетом бонусов.
    :param word: слово, которое располагаем
    :return: Индекс начала слова, начиная с которого слово будет располагаться
    наилучшим образом
    """
    most_expensive_letter_value = 0
    most_expensive_letter_index = None
    best_hint = get_empty_board(15, 15)  # Создаем пустую доску
    center_of_board_by_x = int(len(best_hint[int(len(best_hint) / 2)]) / 2)
    distance_to_bonus = 4  # Расстояние от стартового поля до бонуса x2
    # todo: calculate it for each board
    movement = len(word) - distance_to_bonus
    # На сколько слово может двигаться, оставаясь на стартовом поле

    letters_to_bonus = ''.join([word[:movement], word[-movement:]])
    # Выбираем буквы, которые могут быть на бонусе

    for i in range(len(letters_to_bonus)):
        if LETTERS_VALUES[letters_to_bonus[i]] > most_expensive_letter_value:
            most_expensive_letter_value = LETTERS_VALUES[letters_to_bonus[i]]
            most_expensive_letter_index = i if i < len(letters_to_bonus) / 2 \
                else i + len(word) - len(letters_to_bonus)
            # Находим индекс самой ценной буквы из доступных

    bonus_index = center_of_board_by_x - distance_to_bonus \
        if most_expensive_letter_index < int(len(word) / 2) \
        else center_of_board_by_x + distance_to_bonus

    best_start_index = bonus_index - most_expensive_letter_index

    return best_start_index


# Автор: Матвей
def get_best_hint_for_empty_board(letters: Counter) -> str:
    """
    Ищет лучшее слово, которое можно составить из букв игрока в начале игры.
    :param letters: буквы, которые есть у игрока
    :return: лучшее слово
    """
    best_word = ''
    best_word_value = 0
    best_start_index = None
    best_hint = get_empty_board(15, 15)  # Создаем пустую доску
    center_of_board_by_y = int(len(best_hint) / 2)

    with open(Path(Path.cwd() / 'dictionaries' / DICTIONARY_MAX_7_LETTERS_FILE_PATH),
              'r', encoding='utf-8') as dict_file:
        for line in dict_file:  # Читаем строки из словаря
            word = line[:-1]  # Записываем слово без '\n'
            if is_word_compilable(letters, word):
                # Если слово можно составить из букв игрока
                if len(word) < 5:
                    word_value = calculate_letters_value(word)
                elif len(word) < 8:  # Если слово состоит из 5-7 букв
                    word_start_by_x = arrange_long_word_to_empty_board(word)
                    # Располагаем слово наилучшим образом
                    word_value = calculate_word_value(word, best_hint,
                                                      center_of_board_by_y,
                                                      word_start_by_x)
                    # Считаем ценность слова, при лучшем расположении

                if word_value > best_word_value:  # Если найдено слово лучше
                    best_word = word
                    best_word_value = word_value
                    best_start_index = int((len(best_hint[center_of_board_by_y]) -
                                            len(best_word)) / 2) if len(best_word) < 5 \
                        else word_start_by_x

    for i in range(len(best_word)):
        best_hint[center_of_board_by_y][best_start_index + i] = best_word[i]
    # Вписываем найденое слово в доску

    return best_hint
