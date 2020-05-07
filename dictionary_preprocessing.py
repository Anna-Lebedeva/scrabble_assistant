import re
from collections import Counter
from scrabble_assistant import read_json, get_marked_rows

LETTERS_VALUES_FILENAME = "letters_values.json"
LETTERS_AMOUNT_FILENAME = "letters_amount.json"
BOARD_BONUSES_FILENAME = "board_bonuses.json"
DICTIONARY_FILENAME = "dictionary.txt"


def is_word_correct(word: str) -> bool:
    """
    Проверяет слово на корректность - не содержит ли оно неожиданных символов,
    не содержит ли оно больше букв, чем есть в игре.
    :param word: слово
    :return: true = переданное слово не содержит неожиданных символов
    """

    word = word.lower()
    alphabet = set(read_json(LETTERS_AMOUNT_FILENAME).keys())
    # множество букв, для которых указана стоимость

    for letter in word:
        if letter not in alphabet:
            return False

    letters_amount = read_json(LETTERS_AMOUNT_FILENAME)
    word_letters = Counter(word)

    for letter in word:
        if word_letters[letter] > letters_amount[letter]:
            return False
    return True


# не удалять пока
'''def is_word_fits_in_pattern(sharped_row: [str], word: str) -> bool:
    result = []
    patterns = get_regex_patterns(sharped_row)

    for pattern in patterns:
        found = pattern.findall(word)
        if pattern.findall(word):
            # if pattern.findall(word).pop() == word:
            result.append(pattern.findall(word))
    return bool(result)'''


def is_word_available(letters: Counter, word: str) -> bool:
    """
    Проверяет возможность составить слово из переданных букв
    :param letters: счетчик букв игрока
    :param word: слово
    :return: можно ли составить из переданных букв переданое слово
    """

    word_letters = Counter(word)  # счетчик букв
    for letter in word_letters.keys():
        if letters[letter] < word_letters[letter]:
            return False
    return True


def calculate_word_value(word: str, start_pos: int = None, end_pos: int = None) -> int:
    """
    Считает ценность слова
    :param start_pos: позиция начала слова [y, x]
    :param end_pos: позиция конца слова [y, x]
    :param word: слово в виде строки
    :return: ценность слова
    """

    # разметка ценности полей доски:
    # 0 - обычное поле
    # 1 - х2 за букву
    # 2 - х3 за букву
    # 3 - х2 за слово
    # 4 - х3 за слово
    # 5 - стартовое поле

    # todo: добавить поправку на бонусы

    letters_values = read_json(LETTERS_VALUES_FILENAME)
    return sum([letters_values[letter] for letter in word.lower()])


def get_regex_patterns(sharped_row: [str]) -> [re.Pattern]:
    """
    Получает строку, возвращает паттерны, соответствующие этой строке, для поиска подходящих
    слов в словаре по этому паттерну.
    :param sharped_row: размеченный '#' ряд
    :return: шаблон, по которому можно найти подходящие слова
    """
    prepared_row = []
    patterns = []
    # test_row = ['', '', '', 'а', '#', 'а', '#', '#', '#', '#', '', 'р', '', '', '']

    for cell in range(len(sharped_row)):
        if sharped_row[cell]:  # если в клетке есть символ
            prepared_row.append(sharped_row[cell])
        else:  # если клетка пустая
            prepared_row.append(' ')

    prepared_row = ''.join(prepared_row).split('#')
    # соединяем в строку и нарезаем на подстроки по '#'

    for i in range(len(prepared_row)):
        if len(prepared_row[i]) > 1:
            patterns.append(prepared_row[i])  # отбираем подстроки длинее 1 символа

    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace(' ', '[а-я]?')
    # в пустое место можно вписать любую букву букву а-я или не писать ничего
    # todo: Можно переписать регулярку c помощью одних фигурных скобок

    for i in range(len(patterns)):
        patterns[i] = '^(' + patterns[i] + ')$'
    # Чтобы регулярка не хватала слова, которые удовлетворяют, но выходят за рамки.

    # for i in range(len(patterns)):
    #    patterns[i] = re.compile(patterns[i])
    # компилируем каждый паттерн в регулярное выражение
    # upd. компиляция не понадобится. Но пока не удалять

    return patterns


