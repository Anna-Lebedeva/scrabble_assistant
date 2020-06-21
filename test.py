import time
from collections import Counter
from assistant import scrabble_assistant as sa
from preprocessing.dictionary import\
    prepare_frequency_dictionaries

if __name__ == '__main__':

    test_board = [
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

    # print(20 == calculate_word_value('тотем',
    #                                  transpose_board(test_board), 11, 10))
    # print(8 == calculate_word_value('дуло',
    #                                 transpose_board(test_board), 4, 1))
    # передаем транспонированную доску, тк слово написано по вертикали
    # если доска транспонирована - координаты меняются местами

    # test_marked_board = get_marked_rows(test_board)
    # for iii in range(len(test_marked_board)):
    #     print(test_marked_board[iii])
    # print(get_marked_row(test_board, 12))

    # patterns_, letters_ = get_regex_patterns(
    #     ['', '', 'д', 'а', '', 'а', '#', 'о', '', '#', '', 'р', '', 'к', 'а'])
    # print(patterns_, letters_)

    # print(patterns_[0])

    # print(is_word_fit_to_pattern('прока', patterns_[2]))
    # print(is_word_fit_to_pattern('ок', patterns_[1]))
    # print(is_word_fit_to_pattern('поклажа', patterns_[0]))
    # print(is_word_fit_to_pattern('фрукт', patterns_[0]))

    # test_row = ['', '', 'д', 'а', '', 'а', '#', 'о', '', '#', '', 'р', '', 'к', 'а']
    # print('дама: ' + str(get_word_possible_positions_in_row('дама', test_row)))  # 2
    # print('даг: ' + str(get_word_possible_positions_in_row('даг', test_row)))  # нет
    # print('адам: ' + str(get_word_possible_positions_in_row('адам', test_row)))  # нет
    # print('адама: ' + str(get_word_possible_positions_in_row('адама', test_row)))  # 1
    # print('редара: ' + str(get_word_possible_positions_in_row('редара', test_row)))  # 0
    # print('река: ' + str(get_word_possible_positions_in_row('река', test_row)))  # 11
    # print('шрека: ' + str(get_word_possible_positions_in_row('шрека', test_row)))  # 10
    # print('шре: ' + str(get_word_possible_positions_in_row('шре', test_row)))  # нет
    #
    # print()
    #
    # test_row = ['', '', '', 'в', '', 'р', '#', 'а', '', 'в', '', '', 'в', '', '']
    # print('варвар: ' + str(get_word_possible_positions_in_row('варвар', test_row)))  # 0, 9
    # print('вар: ' + str(get_word_possible_positions_in_row('вар', test_row)))  # 3, 12
    #
    # test_row = ['', 'а', '', 'д', '', 'а', '#', 'а', '', 'д', '', '', 'д', '', '']
    # print('да: ' + str(get_word_possible_positions_in_row('да', test_row)))
    # print('ад: ' + str(get_word_possible_positions_in_row('ад', test_row)))

    # test_board = [
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    # ]

    # # убираем пробелы, они нужны были только для удобства ввода
    for test_row in test_board:
        for test_j in range(len(test_row)):
            if test_row[test_j] == ' ':
                test_row[test_j] = ''

    # t = time.time()
    #
    # # вся магия происходит тут
    # test_hint, test_value = sa.get_hint(test_board, Counter('абвгд'))
    #
    # print('Time = ' + str(time.time() - t) + 's')
    #
    # # доска с подсказкой
    # hint = []
    # for test_i in range(len(test_hint)):
    #     hint.append([])
    #     for test_j in range(len(test_hint[test_i])):
    #         if test_board[test_i][test_j] != '':
    #             hint[test_i].append(test_board[test_i][test_j])
    #         else:
    #             if test_hint[test_i][test_j] == '':
    #                 hint[test_i].append(' ')
    #             else:
    #                 hint[test_i].append(test_hint[test_i][test_j].upper())
    #     print(hint[test_i])
    #
    # print('Hint value = ' + str(test_value))

    # t = time.time()
    # test_hints, test_values = sa.get_n_hints(test_board, Counter('ааелкнм'), 10)
    # print('Time = ' + str(time.time() - t) + 's')
    #
    # for hint_i in range(len(test_hints)):
    #     # доска с подсказкой
    #     hint = []
    #     for test_i in range(len(test_hints[hint_i])):
    #         hint.append([])
    #         for test_j in range(len(test_hints[hint_i][test_i])):
    #             if test_board[test_i][test_j] != '':
    #                 hint[test_i].append(test_board[test_i][test_j])
    #             else:
    #                 if test_hints[hint_i][test_i][test_j] == '':
    #                     hint[test_i].append(' ')
    #                 else:
    #                     hint[test_i].append(test_hints[hint_i][test_i][test_j].upper())
    # print('Ценность подсказок: ' + str(test_values))

    # f2 = open('resources/dictionaries/new_dictionary14.txt', 'w',
    #           encoding='utf-8')
    # with open('resources/dictionaries/new_dictionary15.txt', 'r',
    #           encoding='utf-8') as dictionary:
    #     for line in dictionary:
    #         if len(line) <= 14 + 1:
    #             f2.write(line)
    # f2.close()

    prepare_frequency_dictionaries('resources/dictionaries/nouns.txt')
