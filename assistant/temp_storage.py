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


# author - Matvey
# todo: удалить или все же пригодится?
def calculate_letters_value(word: str) -> int:
    """
    Считает ценность слова, без учета бонусов.
    :param word: слово, ценность которого нужно посчитать
    :return: ценность слова, без учета бонусов
    """

    return sum([LETTERS_VALUES[letter] for letter in word])


# author - Matvey
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
