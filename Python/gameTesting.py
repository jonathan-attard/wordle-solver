import numpy as np

from wordle import *
import time

player_words = get_words()
game_words = get_words()


def true_random_play():
    round_taken = 0
    w = Wordle()
    for i in range(6):

        word = random.choice(player_words)
        marking, done = w.guess(word)

        if done:
            # print("COMPLETE in", str(i + 1), "rounds")
            round_taken = i + 1
            break

    return round_taken


def random_play():
    round_taken = 0

    w = Wordle(chosen_word=random.choice(all_words))
    all_words_temp = copy.deepcopy(all_words)
    for i in range(6):
        word = random.choice(all_words_temp)
        # print("GUESS:", word)
        marking, done = w.guess(word)
        # print(marking)

        if done:
            # print("COMPLETE in", str(i + 1), "rounds")
            round_taken = i + 1
            break

        # updating all words
        all_words_temp = update_current_words_2(all_words_temp, marking, word)
        # print("REDUCED TO:", len(all_words_temp))

    return round_taken


# random_play()

# words_rated = get_words_rated()
# def pick_freq(word_list):
#     picked_word = None
#
#     for word in words_rated:
#         word = expand_word(word)
#         if word in word_list:
#             picked_word = word
#             break
#
#     return picked_word


# EXTRA (new better freq 2)
def get_freq_letters(word_list, word_length=5):
    num_words = len(word_list)
    # print(num_words)
    # frequencies = get_letter_frequency(word_list, word_length=5)
    # print(frequencies)
    # return word_list[0]

    # Getting all letter frequencies

    letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
                               dtype=int)  # List of frequencies with the letter in that particular position
    letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
    for word in word_list:
        for i in range(len(word)):
            letter = word[i]
            letter_freq_pos[i][ALPHABET.index(letter)] += 1
            letter_freq[ALPHABET.index(letter)] += 1
    letter_freq_pos = letter_freq_pos / num_words
    letter_freq = letter_freq / num_words

    return letter_freq_pos, letter_freq


def pick_better_freq2(word_list, letter_freq_pos, letter_freq, word_length=5):
    # Getting ratings of all words
    best_score = 0
    best_word = word_list[0]
    for word in word_list:
        word_unique = np.unique(word)

        rating = 0
        for i in range(len(word_unique)):
            letter = word_unique[i]
            rating += letter_freq[ALPHABET.index(letter)]
            rating += letter_freq_pos[i][ALPHABET.index(letter)] * 3

            if rating > best_score:
                best_score = rating
                best_word = word

    return best_word


def pick_better_freq(word_list, word_length=5):
    num_words = len(word_list)
    # frequencies = get_letter_frequency(word_list, word_length=5)
    # print(frequencies)
    # return word_list[0]

    # Getting all letter frequencies

    letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
                               dtype=int)  # List of frequencies with the letter in that particular position
    letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
    for word in word_list:
        for i in range(len(word)):
            letter = word[i]
            letter_freq_pos[i][ALPHABET.index(letter)] += 1
            letter_freq[ALPHABET.index(letter)] += 1
    letter_freq_pos = letter_freq_pos / num_words
    letter_freq = letter_freq / num_words

    # Getting ratings of all words
    best_score = 0
    best_word = []
    for word in word_list:
        word_unique = np.unique(word)

        rating = 0
        for i in range(len(word_unique)):
            letter = word_unique[i]
            rating += letter_freq[ALPHABET.index(letter)]
            rating += letter_freq_pos[i][ALPHABET.index(letter)] * 3

            if rating > best_score:
                best_score = rating
                best_word = word

    return best_word


def pick_better_freq_wordFreq(word_list, word_length=5):
    num_words = len(word_list)
    # frequencies = get_letter_frequency(word_list, word_length=5)
    # print(frequencies)
    # return word_list[0]

    # Getting all letter frequencies

    letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
                               dtype=int)  # List of frequencies with the letter in that particular position
    letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
    for word in word_list:
        for i in range(len(word)):
            letter = word[i]
            letter_freq_pos[i][ALPHABET.index(letter)] += 1
            letter_freq[ALPHABET.index(letter)] += 1
    letter_freq_pos = letter_freq_pos / num_words
    letter_freq = letter_freq / num_words

    # Getting ratings of all words
    best_score = 0
    best_word = []
    for word in word_list:
        word_unique = np.unique(word)

        rating = 0
        for i in range(len(word_unique)):
            letter = word_unique[i]
            rating += letter_freq[ALPHABET.index(letter)]
            rating += letter_freq_pos[i][ALPHABET.index(letter)] * 3
            rating += frequency_words[ex_toString(word)]  # all_words.index(word)

            if rating > best_score:
                best_score = rating
                best_word = word

    return best_word


def frequent_play():
    round_taken = 0

    w = Wordle(chosen_word=random.choice(all_words))
    all_words_temp = copy.deepcopy(all_words)
    for i in range(6):
        word = pick_better_freq(all_words_temp)
        # print("GUESS:", word)
        marking, done = w.guess(word)
        # print(marking)

        if done:
            # print("COMPLETE in", str(i + 1), "rounds")
            round_taken = i + 1
            break

        # updating all words
        all_words_temp = update_current_words_2(all_words_temp, marking, word)
        # print("REDUCED TO:", len(all_words_temp))

    return round_taken


def explore_pick(word_list, found_letters):
    # word_list=all_words

    word_list_temp = []
    lowest_count = 1000
    best_unique_count = 0

    # for word in word_list:
    #     unique_letters = len(np.unique(word))
    #     if unique_letters > best_unique_count:
    #         best_unique_count = unique_letters
    # for word in word_list:
    #     unique_letters = len(np.unique(word))
    #     if unique_letters == best_unique_count:
    #         word_list_temp.append(word)

    for word in all_words:
        count_letters = 0
        for letter in word:
            if letter in found_letters:
                count_letters += 1
        unique_letters = len(np.unique(word))
        # print(unique_letters)

        if count_letters < lowest_count or unique_letters > best_unique_count:  # count_letters < lowest_count or
            lowest_count = count_letters
            best_unique_count = unique_letters
            word_list_temp.clear()
            word_list_temp.append(word)
        elif count_letters == lowest_count and unique_letters == best_unique_count:  # count_letters == lowest_count and
            word_list_temp.append(word)

    # print(word_list_temp)
    if word_list_temp:
        # picked_word = pick_better_freq(word_list_temp)
        letter_freq_pos, letter_freq = get_freq_letters(word_list)
        picked_word = pick_better_freq2(word_list_temp, letter_freq_pos, letter_freq)
        # print("PICKED WORD", picked_word)
    else:
        picked_word = pick_better_freq(word_list)
    # print("PICKED WORD", picked_word)

    return picked_word


def explore_play():
    round_taken = 0
    w = Wordle(chosen_word=random.choice(all_words))
    all_words_temp = copy.deepcopy(all_words)
    found_letters = []
    for i in range(6):
        if i == 1 or i == 2 or i == 3:
            word = explore_pick(all_words_temp, found_letters)
        else:
            word = pick_better_freq(all_words_temp)
        marking, done = w.guess(word)

        for i in range(len(marking)):
            if word[i] not in found_letters:
                found_letters.append(word[i])

        if done:
            round_taken = i + 1
            break

        all_words_temp = update_current_words_2(all_words_temp, marking, word)

    return round_taken


def better_explore_play():
    round_taken = 0
    w = Wordle(chosen_word=random.choice(all_words))
    all_words_temp = copy.deepcopy(all_words)
    found_letters = []
    letters_in = []
    for i in range(6):
        # print(len(letters_in))
        if len(letters_in) <= 4 and i <= 3:
            word = explore_pick(all_words_temp, found_letters)
        else:
            word = pick_better_freq(all_words_temp)
        marking, done = w.guess(word)

        for i in range(len(marking)):
            if marking[i] == Mark.PERFECT or marking[i] == Mark.GOOD:  # Adding met letters that are correct
                if word[i] not in letters_in:
                    letters_in.append(word[i])
            if word[i] not in found_letters:  # Adding all letters encountered
                found_letters.append(word[i])

        if done:
            round_taken = i + 1
            break

        all_words_temp = update_current_words_2(all_words_temp, marking, word)

    return round_taken


def compute_results(function, name, max_games=1000):
    sum = 0
    count = 0
    for i in range(max_games):
        res = function()
        if res == 0:
            continue
        sum += res
        count += 1
    if count == 0:
        avg = 0
    else:
        avg = sum / count
    print("Average rounds of " + name + " =", avg, " and games completed:", count / max_games)


def frequent_play_wordFreq():
    round_taken = 0

    w = Wordle(chosen_word=random.choice(all_words))
    all_words_temp = copy.deepcopy(all_words)
    for i in range(6):
        word = pick_better_freq_wordFreq(all_words_temp)
        # print("GUESS:", word)
        marking, done = w.guess(word)
        # print(marking)

        if done:
            # print("COMPLETE in", str(i + 1), "rounds")
            round_taken = i + 1
            break

        # updating all words
        all_words_temp = update_current_words_2(all_words_temp, marking, word)
        # print("REDUCED TO:", len(all_words_temp))

    return round_taken


# compute_results(true_random_play, "true random play")
# compute_results(random_play, "random play with word filtering")
# compute_results(frequent_play, "frequency play with word filtering")
# compute_results(explore_play, "explore play with better word filtering")
compute_results(better_explore_play, "better explore play with better word filtering")
# compute_results(frequent_play_wordFreq, "frequency play with word filtering and considering word frequencies in corpus")

def test_fast():
    print(len(all_words))

    sizus = len(all_words)

    # start = time.time()
    # for i in range(len(all_words)):
    #     w = Wordle(chosen_word=random.choice(all_words))
    #     # print(w)
    # print(f'Time: {time.time() - start}')

    # start = time.time()
    # w = Wordle(chosen_word=random.choice(all_words))
    # for i in range(len(all_words)):
    #     w.guess("testa")
    #     # print(w)
    # print(f'Time: {time.time() - start}')

    start = time.time()
    for i in range(len(all_words)):
        print(i)
        for j in range(sizus):
            pass
            w = Wordle(chosen_word="testh")
            w.guess("testu")
        # print(w)
    print(f'Time: {time.time() - start}')


# test_fast()
