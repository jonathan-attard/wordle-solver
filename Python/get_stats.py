import copy
import math
import time

import numba

from utility import *
from wordle import *
from tqdm import tqdm
import pandas as pd
import concurrent.futures
from concurrent import futures
import itertools
import pprint
import json
from numba import jit, cuda


class MinAverage:
    def __init__(self):
        self.patterns = Pattern()
        self.words = get_words()

    def getRating(self, word, word_list, pattern):  # Gets minimum rating of average
        best_rating = math.inf
        best_word = []

        for word in word_list:
            sum_words = 0
            for p in self.patterns:
                new_words = update_current_words_2(word_list, pattern, word)
                sum_words += len(new_words)
            rating = sum_words / len(self.patterns)

        return best_word


# pattern_word = []
# for p in patterns:
#     new_words = update_current_words_2(words, p, expand_word("unita"))
#     # pattern_word.append(len(new_words))
#
#     pbar = tqdm(total=len(new_words), desc="'Unita' Pattern #" + str(p))
#     best_rating = math.inf
#     best_word = []
#     for word in new_words:  # Iterating over
#         sum_words = 0
#         for p2 in patterns:
#             new_words2 = update_current_words_2(new_words, p2, word)
#             sum_words += len(new_words2)
#         rating = sum_words / len(patterns)
#         if rating < best_rating:
#             best_word = word
#             best_rating = math.inf
#
#         # print(res)
#         pbar.update(1)
#     print("PATTERN #" + str(p), best_word, best_rating)
# print(pattern_word)

def getAvaliableLetters(word, pattern):
    avaliable_letters = [[] for i in range(patterns.pattern_len)]

    num_letter_occurrence = {}  # Number of occurrences
    unique_letters = np.unique(word)
    concluded = []  # We know the number of occurrences for a letter
    # Check if there is a case where a letter has 'good' and another 'blank'
    for i in range(len(pattern)):
        letter = word[i]
        # for j in range(len(marking)):
        if pattern[i] == Mark.GOOD or pattern[i] == Mark.PERFECT:  # If marked with good, add the number
            if letter not in num_letter_occurrence:
                num_letter_occurrence[letter] = 1
            elif letter in num_letter_occurrence:
                num_letter_occurrence[letter] += 1
        elif pattern[i] == Mark.BLANK:
            if letter not in concluded:
                concluded.append(letter)

    # print(num_letter_occurrence)
    # print(concluded)

    avaliable_letters = [[] for i in range(patterns.pattern_len)]

    for i in range(len(pattern)):
        if pattern[i] == Mark.GOOD:
            temp_alph = ALPHABET.copy()
            temp_alph.remove(word[i])
            avaliable_letters[i] = temp_alph
        elif pattern[i] == Mark.PERFECT:
            avaliable_letters[i] = [word[i]]

    # print(avaliable_letters)
    return num_letter_occurrence, concluded, avaliable_letters


def computeAvaliableLetters():
    word_pattern_selection = {}
    pbar = tqdm(total=len(words))
    for word in words:
        word_pattern_selection[word_hash[ex_toString(word)]] = {}
        for pattern in patterns:
            word_pattern_selection[word_hash[ex_toString(word)]][patterns.encodePattern(pattern)] = getAvaliableLetters(
                word, pattern)
        pbar.update(1)
    pbar.close()
    with open("word_pattern_selection.pkl", "wb") as f:
        pickle.dump(word_pattern_selection, f)





patterns = Pattern()
words = get_words()
word_hash = getWordsHash(words=words)


# if __name__ == '__main__':
#     pbar = tqdm(total=len(words))
#     for word in words:
#         with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
#             filter_function = itertools.product([word], patterns, [words])
#             results_ = executor.map(update_current_words_tuple, filter_function)
#             for r in results_:
#                 pass
#         pbar.update(1)

# @cuda.jit
def pick_freq(word_list, letter_freq_pos=None, letter_freq=None, parameters=None):
    # word_length = 5

    # Getting all letter frequencies
    if letter_freq is None and letter_freq_pos is None:
        (letter_freq, letter_freq_pos) = get_freq_pos(word_list)
        # letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
        #                            dtype=int)  # List of frequencies with the letter in that particular position
        # letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
        # for word in word_list:
        #     for i in range(len(word)):
        #         letter = word[i]
        #         letter_freq_pos[i][ALPHABET.index(letter)] += 1
        #         letter_freq[ALPHABET.index(letter)] += 1

    if parameters is None:
        strength_letter_pos = 0.5
        strength_freq = 1
    else:
        strength_freq = parameters[0]
        strength_letter_pos = parameters[1]

    # Getting ratings of all words
    best_score = 0
    best_word = []
    for word in word_list:
        word_unique = np.unique(word)
        rating = 0

        for letter in word_unique:
            rating += letter_freq[ALPHABET.index(letter)] * strength_freq

        for i in range(len(word)):
            letter = word[i]
            # rating += letter_freq[ALPHABET.index(letter)]
            rating += letter_freq_pos[i][ALPHABET.index(letter)] * strength_letter_pos

        if rating > best_score:
            best_score = rating
            best_word = word

    # print(best_word, word_list, letter_freq_pos, letter_freq)
    if len(best_word) == 0:
        best_word = word_list[0]

    return best_word


def pickExplore(word_list, round, found_letters, letters_in):
    if len(letters_in) <= 4 and round <= 3:
        word_list_temp = []
        lowest_count = math.inf
        best_unique_count = 0

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

        if word_list_temp:
            picked_word = pick_freq(word_list_temp)
        else:
            picked_word = pick_freq(word_list)

    else:
        picked_word = pick_freq(word_list)

    return picked_word


def pickMinAverage(word_list):
    best_word = None
    smallest_num_words = math.inf
    list_of_best_words = []
    final_word_list = []

    # pbar = tqdm(total=len(word_list))
    for word in words[:100]:  # words[:100]:
        num_words = 0
        for pattern in patterns:
            new_word_list = update_current_words_len(word_list, pattern, word)
            num_words += new_word_list  # len(new_word_list)

        if num_words < smallest_num_words:
            best_word = word
            # final_word_list = new_word_list
            smallest_num_words = num_words
        # pbar.update(1)
    # pbar.close()

    return best_word  # , smallest_num_words, final_word_list


def getTree(word_list, word, pickerFunction):
    pattern_words = {}
    for pattern in patterns:
        words_in_pattern = update_current_words_2(word_list, pattern, word)
        if len(words_in_pattern) == 0:
            continue
        if pattern == [2, 2, 2, 2, 2]:
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        pattern_words[str(tuple(pattern))] = {}

        if len(words_in_pattern) == 1:
            temp_dict = {str((2, 2, 2, 2, 2)): True}
            pattern_words[str(tuple(pattern))][ex_toString(words_in_pattern[0])] = temp_dict
        else:
            # print(words_in_pattern)
            best_word = pickerFunction(words_in_pattern)
            pattern_words[str(tuple(pattern))][ex_toString(best_word)] = getTree(words_in_pattern, best_word,
                                                                                 pickerFunction)

    return pattern_words


def calculate_tree_guesses(tree_dict, count=0):
    global losses, wins
    if tree_dict is True:
        if count > 5:
            losses += 1
        else:
            wins += 1
        return count

    sum_guesses = 0
    num_guesses = 0

    word = list(tree_dict.keys())[0]

    if tree_dict[word] is False:  # Finished early, game lost
        losses += 1
        return 0

    patterns = tree_dict[word]

    for pattern in patterns:
        temp_count = calculate_tree_guesses(tree_dict[word][pattern], count=count + 1)
        sum_guesses += temp_count
        num_guesses += 1

    return sum_guesses / num_guesses


from gameTesting import *


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


def getTreeExplore(word_list, word, found_letters=None, letters_in=None, round=1):
    if round == 5:
        return False

    if letters_in is None:
        letters_in = []
    if found_letters is None:
        found_letters = []
    pattern_words = {}

    for pattern in patterns:
        words_in_pattern = update_current_words_2(word_list, pattern, word)
        if len(words_in_pattern) == 0:
            continue
        if pattern == [2, 2, 2, 2, 2]:
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        pattern_words[str(tuple(pattern))] = {}

        if len(words_in_pattern) == 1:
            temp_dict = {str((2, 2, 2, 2, 2)): True}
            pattern_words[str(tuple(pattern))][ex_toString(words_in_pattern[0])] = temp_dict
            # print("REACHED")
        else:
            # print(words_in_pattern)
            # best_word = pickerFunction(words_in_pattern)

            # Updating letters_in and found_letters from pattern and best_word
            temp_letters_in = copy.deepcopy(letters_in)
            temp_found_letters = copy.deepcopy(found_letters)
            for i in range(len(pattern)):
                if pattern[i] == Mark.PERFECT or pattern[i] == Mark.GOOD:  # Adding met letters that are correct
                    if word[i] not in temp_letters_in:
                        temp_letters_in.append(word[i])
                if word[i] not in temp_found_letters:  # Adding all letters encountered
                    temp_found_letters.append(word[i])

            if len(letters_in) <= 4 and round <= 3:
                best_word = explore_pick(words_in_pattern, temp_found_letters)
            else:
                best_word = pick_better_freq(words_in_pattern)
            # marking, done = w.guess(word)

            # # Updating letters_in and found_letters from pattern and best_word
            # temp_letters_in = copy.deepcopy(letters_in)
            # temp_found_letters = copy.deepcopy(found_letters)
            # for i in range(len(pattern)):
            #     if pattern[i] == Mark.PERFECT or pattern[i] == Mark.GOOD:  # Adding met letters that are correct
            #         if word[i] not in temp_letters_in:
            #             temp_letters_in.append(word[i])
            #     if word[i] not in temp_found_letters:  # Adding all letters encountered
            #         temp_found_letters.append(word[i])

            pattern_words[str(tuple(pattern))][ex_toString(best_word)] = getTreeExplore(words_in_pattern, best_word,
                                                                                        found_letters=temp_found_letters,
                                                                                        letters_in=temp_letters_in,
                                                                                        round=round + 1)

    return pattern_words


all_words = get_words()


def get_freq_pos(word_list):
    word_length = 5

    # Getting all letter frequencies
    letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
                               dtype=float)  # List of frequencies with the letter in that particular position
    letter_freq = np.zeros(len(ALPHABET), dtype=float)  # List of frequencies for letter in general
    for word in word_list:
        for i in range(len(word)):
            letter = word[i]
            letter_freq_pos[i][ALPHABET.index(letter)] += 1
            letter_freq[ALPHABET.index(letter)] += 1
    # Normalising
    for pos in range(len(letter_freq_pos)):
        letter_freq_pos[pos] /= (len(word_list))
    letter_freq /= (len(word_list) * word_length)
    return letter_freq, letter_freq_pos


def fullExporePick(word_list, num_letter_occurrence, concluded, avaliable_letters, letter_freq, letter_freq_pos,
                   all_words=None, strength_params=None):
    if all_words is None:
        all_words = word_list

    word_length = 5

    if strength_params is None:
        strength_freq = 0
        strength_letter_pos = 0
        strength_concluded = 0
        strength_occur = 0
        strength_perfect = 0
        strength_available = 0
    else:
        (strength_freq, strength_letter_pos, strength_concluded, strength_occur, strength_perfect,
         strength_available) = strength_params

    # Getting ratings of all words
    best_score = 0
    best_word = []
    for word in all_words:
        rating = 0
        word_unique = np.unique(word)
        for letter in word_unique:
            rating += letter_freq[ALPHABET.index(letter)] * strength_freq

        for i in range(len(word)):
            letter = word[i]
            rating += letter_freq_pos[i][ALPHABET.index(letter)] * strength_letter_pos

            if letter in concluded:
                rating -= (1 / word_length) * strength_concluded
            elif letter in num_letter_occurrence:
                if num_letter_occurrence[letter] >= word.count(letter):
                    rating -= (1 / word_length) * strength_occur
            if len(avaliable_letters[i]) == 0 and avaliable_letters[i][0] == letter:
                rating -= (1 / word_length) * strength_perfect
            if letter in avaliable_letters[i] and len(avaliable_letters[i]) != 0:
                rating += (1 / word_length) * strength_available
        if rating > best_score:
            best_score = rating
            best_word = word

    # print(best_word, word_list, letter_freq_pos, letter_freq)
    if len(best_word) == 0:
        best_word = word_list[0]

    return best_word


# pbar = tqdm(total=len(patterns))


def getTreeExploreFull(word_list, word, num_letter_occurrence=None, concluded=None, avaliable_letters=None, round=1,
                       explore_finished=False, parameters=None):
    if round == 6:  # Stop depth -> lost
        return False

    # global pbar
    global all_words
    if num_letter_occurrence is None:
        num_letter_occurrence = {}
    if concluded is None:
        concluded = []
    if avaliable_letters is None:
        avaliable_letters = [copy.deepcopy(ALPHABET) for i in range(patterns.pattern_len)]

    # Getting letter frequencies
    (letter_freq, letter_freq_pos) = get_freq_pos(word_list)

    pattern_words = {}

    for pattern in patterns:
        if round == 1:
            pass
            # pbar.update(1)

        words_in_pattern, num_letter_occurrence_pretemp, concluded_pretemp = update_current_words_2(word_list, pattern,
                                                                                                    word,
                                                                                                    more_return=True)
        if len(words_in_pattern) == 0:
            continue
        if pattern == [2, 2, 2, 2, 2]:
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        pattern_words[str(tuple(pattern))] = {}

        if len(words_in_pattern) == 1:
            temp_dict = {str((2, 2, 2, 2, 2)): True}
            pattern_words[str(tuple(pattern))][ex_toString(words_in_pattern[0])] = temp_dict
        else:
            if not explore_finished:
                num_letter_occurrence_temp = num_letter_occurrence.copy()
                concluded_temp = concluded.copy()  # We know the number of occurrences for a letter
                avaliable_letters_temp = avaliable_letters.copy()
                explore_finished_temp = explore_finished

                # Updating temporary known information
                # Marking avaliable letters of current word-pattern
                for i in range(len(pattern)):
                    if pattern[i] == Mark.PERFECT:
                        avaliable_letters_temp[i] = [word[i]]
                    elif pattern[i] == Mark.GOOD:
                        if word[i] in avaliable_letters_temp[i]:
                            avaliable_letters_temp[i].remove(word[i])
                    # No need for blank, as blank give us information about the number of the same letter within the word

                # Getting concluded and num_letter_occurance of current word-pattern
                # num_letter_occurrence_pretemp = {}  # Number of occurrences

                for i in range(len(pattern)):
                    letter = word[i]
                    # for j in range(len(marking)):
                    if pattern[i] == Mark.GOOD or pattern[i] == Mark.PERFECT:  # If marked with good, add the number
                        num_letter_occurrence_pretemp[letter] = 1 if letter not in num_letter_occurrence_pretemp else \
                            num_letter_occurrence_pretemp[letter] + 1

                # Updating pretemps
                for letter in concluded_pretemp:
                    if letter not in concluded_temp:
                        concluded_temp.append(letter)
                for letter, count in num_letter_occurrence_pretemp.items():
                    if letter not in num_letter_occurrence_temp:  # If not present add it
                        num_letter_occurrence_temp[letter] = count
                    else:  # If within, only keep the largest number
                        if count > num_letter_occurrence_temp[letter]:
                            num_letter_occurrence_temp[letter] = count
                    # Updating concluded; if all count of available letters is equal, then concluded
                    current_letter_counter = 0
                    for letters in avaliable_letters_temp:
                        if letter in letters:
                            current_letter_counter += 1
                    if current_letter_counter == count:
                        concluded_temp.append(letter)

                if sum(list(num_letter_occurrence_temp.values())) <= 5 and round <= 4:
                    best_word = fullExporePick(words_in_pattern, num_letter_occurrence_temp, concluded_temp,
                                               avaliable_letters_temp, letter_freq, letter_freq_pos,
                                               all_words=all_words, strength_params=parameters)
                else:
                    best_word = pick_freq(words_in_pattern, letter_freq=letter_freq, letter_freq_pos=letter_freq_pos)
                    explore_finished_temp = True

                pattern_words[str(tuple(pattern))][ex_toString(best_word)] = getTreeExploreFull(words_in_pattern,
                                                                                                best_word,
                                                                                                num_letter_occurrence=num_letter_occurrence_temp,
                                                                                                concluded=concluded_temp,
                                                                                                avaliable_letters=avaliable_letters_temp,
                                                                                                round=round + 1,
                                                                                                explore_finished=explore_finished_temp,
                                                                                                parameters=parameters)
            else:
                best_word = pick_freq(words_in_pattern, letter_freq=letter_freq, letter_freq_pos=letter_freq_pos)

                pattern_words[str(tuple(pattern))][ex_toString(best_word)] = getTreeExploreFull(words_in_pattern,
                                                                                                best_word,
                                                                                                round=round + 1,
                                                                                                explore_finished=explore_finished,
                                                                                                parameters=parameters)

    return pattern_words


# losses = 0
# wins = 0
# words = words[:1000]
# start_word = pick_freq(words)
# res = {ex_toString(start_word): getTree(words, start_word, pick_freq)}
# ress = calculate_tree_guesses(res)
# print(ress)

# res2 = {ex_toString(start_word): getTree(words, start_word, pickMinAverage)}
# ress2 = calculate_tree_guesses(res2)
# print(ress2)
# pp = pprint.PrettyPrinter(depth=6)
# pp.pprint(res)

losses = 0
wins = 0
words = words[:]
start_word = pick_freq(words)

# Pick min average
# res = {ex_toString(start_word): getTree(words, start_word, pickMinAverage)}
# # pp = pprint.PrettyPrinter(depth=6)
# # pp.pprint(res)
# ress = calculate_tree_guesses(res)
# print(ress, wins / (wins + losses))

# Pick frequency
# res = {ex_toString(start_word): getTree(words, start_word, pick_freq)}
# pp.pprint(res)
# res = loadJson("better_freq_word_trees.json")
# ress = calculate_tree_guesses(res)
# print(ress, wins / (wins + losses))

# BetterExploreFrequency
# start = time.time()
# res = {ex_toString(start_word): getTreeExplore(words, start_word)}
# # pp = pprint.PrettyPrinter(depth=6)
# # pp.pprint(res)
# end = time.time() - start
# print(end)
# ress = calculate_tree_guesses(res)
# print(ress, wins / (wins + losses))

best_wr_params = {}  # {parameter: win rate}
best_guess_params = {}  # {parameter: average guess}


# Better Explore Frequency Full
def playBetterFrequencyFull(parameters=None, save=True):
    if parameters is None:
        parameters = (0.5, 0, 0.5, 0, 0.5, 0) # Found to be the best
    global best_guess_params, best_wr_params
    res = {ex_toString(start_word): getTreeExploreFull(words, start_word, parameters=parameters)}
    # pbar.close()
    # pp = pprint.PrettyPrinter(depth=6)
    # pp.pprint(res)
    # if save:
    #     saveJson("BetterExploreFrequencyFullBEST.json", res)
    # res = loadJson("BetterExploreFrequencyFullBEST.json")
    avg_g = calculate_tree_guesses(res)
    print("Average guess", avg_g, "Win ratio: ", wins / (wins + losses), "Parameters:", parameters)

    best_wr_params[parameters] = wins / (wins + losses)
    best_guess_params[parameters] = avg_g

    return avg_g, wins / (wins + losses)


# calc_time(playBetterFrequencyFull)

def test_actual_game():
    # if expand_word("żiedtx") in all_words:
    #     print("TRUE")
    new_words = update_current_words(all_words, [Mark.BLANK, Mark.PERFECT, Mark.BLANK, Mark.BLANK, Mark.PERFECT],
                                     expand_word('tirna'))
    print(new_words)
    word = pick_freq(new_words)
    print(word)
    #
    # new_words = update_current_words(new_words, [Mark.BLANK, Mark.BLANK, Mark.BLANK, Mark.PERFECT, Mark.BLANK], expand_word('lestu'))
    # print(new_words)
    # # word = pick_freq(new_words)
    # # print(word)
    #
    # new_words = update_current_words(new_words, [Mark.BLANK, Mark.BLANK, Mark.PERFECT, Mark.GOOD, Mark.GOOD]
    #                                  , expand_word('obdiet'))
    # print(new_words)
    # word = pick_freq(new_words)
    # print(word)

    # new_words = update_current_words(new_words, [Mark.BLANK, Mark.PERFECT, Mark.PERFECT, Mark.PERFECT, Mark.PERFECT],
    #                                  word)
    # print(new_words)
    # word = pick_freq(new_words)
    # print(word)
# test_actual_game()


from multiprocessing import Process
from multiprocessing import Pool

if __name__ == '__main__':
    exit()

    num_diff = [0, 0.5, 1, 1.5]
    # num_diff = [0, 0.5]
    num_parameters = 6

    processes = []

    parameter_combo = itertools.product(num_diff, num_diff, num_diff, num_diff, num_diff, num_diff)
    # parameter_combo = [(0.5, 0, 0.5, 0, 0, 0), (0.5, 0, 0.5, 0, 0.5, 0), (1, 0, 1, 0, 0.5, 0)]

    Games = []

    pool = Pool(processes=6)  # use all available cores, otherwise specify the number you want as an argument
    for parameter in parameter_combo:
        # print(parameter)
        # playBetterFrequencyFull(parameters=parameter)

        # p = Process(target=playBetterFrequencyFull, args=(parameter, ))
        # p.start()
        # processes.append(p)

        pool.apply_async(playBetterFrequencyFull, args=(parameter,))

    # for p in processes:
    #     p.join()
    pool.close()
    pool.join()

    # saveJson("BestWrParams.json", best_wr_params)
    # saveJson("BestAvgGuessParams.json", best_guess_params)