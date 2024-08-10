import numpy as np

from numba import jit, cuda
from wordle import *
import time
import itertools
import json
import math
from tqdm import tqdm


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


def pick_better_freq(word_list, word_length=5):
    # Getting all letter frequencies

    letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
                               dtype=int)  # List of frequencies with the letter in that particular position
    letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
    for word in word_list:
        for i in range(len(word)):
            letter = word[i]
            letter_freq_pos[i][ALPHABET.index(letter)] += 1
            letter_freq[ALPHABET.index(letter)] += 1
    letter_freq_pos = letter_freq_pos
    letter_freq = letter_freq

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


# def patterns():
#     type_number = 3
#     word_size = 5
#     combinations = [x for x in itertools.product(range(type_number),
#                                                  repeat=word_size)]  # https://www.daniweb.com/programming/software-development/threads/435159/n-number-for-nested-for-loops
#
#     pattern_words = {}
#
#     first_word = expand_word("unita")
#
#     for pattern in combinations:
#         pattern_words[pattern] = update_current_words_2(all_words, list(pattern), first_word)
#
#         if not pattern_words[pattern]:
#             continue
#         pattern_words2 = {}
#         next_best = pick_better_freq(pattern_words[pattern])
#         for pattern2 in combinations:
#             pattern_words2[pattern2] = update_current_words_2(pattern_words[pattern], list(pattern2), next_best)
#         print(pattern_words2)
#
#
#
#     print(pattern_words)


def better_freq_perfect_expolore():
    round_taken = 0
    w = Wordle()
    all_words_temp = copy.deepcopy(get_player_words())
    sure_letters = []
    encountered_letters = []
    for i in range(5):
        sure_letters.append([])
        encountered_letters.append([])
    for i in range(6):
        word = pick_better_freq(all_words_temp)
        marking, done = w.guess(word)

        for i in range(len(marking)):
            if marking[i] == Mark.PERFECT:
                sure_letters[i] = word[i]

        if done:
            round_taken = i + 1
            break

        all_words_temp = update_current_words_2(all_words_temp, marking, word)

    return round_taken


combinations = [x for x in itertools.product(range(3),
                                             repeat=5)]  # https://www.daniweb.com/programming/software-development/threads/435159/n-number-for-nested-for-loops

json_word_trees = "word_trees.json"  # {starting_word: {pattern1: {word1: {patterns}, word2: {patterns}}, pattern2: {word1: {patterns}, word2: {patterns}} }


# TOO MUCH TIME AND MEMORY
def get_patterns_and_words(words, word, word_size=5):
    pattern_words = {}
    # pbar2 = tqdm(total=len(combinations))
    for pattern in combinations:
        # pbar2.update(1)
        words_in_pattern = update_current_words_2(words, list(pattern), word)
        if not words_in_pattern:
            continue

        if pattern == (2, 2, 2, 2, 2):
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        for w in words_in_pattern:
            if str(pattern) not in pattern_words:
                pattern_words[str(pattern)] = {}
            pattern_words[str(pattern)][ex_toString(w)] = get_patterns_and_words(words_in_pattern, w)

    return pattern_words


def get_enthropy(words, word, word_size=5):
    # pattern_words = {}

    E = 0
    # Get all words for every pattern
    for pattern in combinations:
        words_in_pattern_len = update_current_words_len(words, list(pattern), word)
        if words_in_pattern_len == 0:
            continue

        # if pattern == (2, 2, 2, 2, 2):
        #     pattern_words[str((2, 2, 2, 2, 2))] = True
        #     continue

        # pattern_words[str(pattern)] = words_in_pattern
        P = words_in_pattern_len / len(words)
        E += P * math.log(1 / P, 2)

    return E


def get_best_enthropy(words):
    best_rat = 0
    best_word = words[0]
    for word in words:
        E = get_enthropy(words, word)
        print(E)
        if E > best_rat:
            best_rat = E
            best_word = word

    return best_word


def get_tree(words, word, word_size=5):
    pattern_words = {}

    for pattern in combinations:
        words_in_pattern = update_current_words_2(words, list(pattern), word)
        if len(words_in_pattern) == 0:
            continue

        if pattern == (2, 2, 2, 2, 2):
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        pattern_words[str(pattern)] = {}

        if len(words_in_pattern) == 1:
            temp_dict = {}
            temp_dict[str((2, 2, 2, 2, 2))] = True
            pattern_words[str(pattern)][ex_toString(words_in_pattern[0])] = temp_dict
        else:
            print(words_in_pattern)
            best_word = get_best_enthropy(words_in_pattern)
            print("best_word", best_word)
            pattern_words[str(pattern)][ex_toString(best_word)] = get_tree(words_in_pattern, best_word)

    return pattern_words


def get_tree_min_average(words, word, word_size=5):
    pattern_words = {}

    for pattern in combinations:
        words_in_pattern = update_current_words_2(words, list(pattern), word)
        if len(words_in_pattern) == 0:
            continue

        if pattern == (2, 2, 2, 2, 2):
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        pattern_words[str(pattern)] = {}

        if len(words_in_pattern) == 1:
            temp_dict = {}
            temp_dict[str((2, 2, 2, 2, 2))] = True
            pattern_words[str(pattern)][ex_toString(words_in_pattern[0])] = temp_dict
        else:
            # print(words_in_pattern)
            best_word = get_best_min_averge(words_in_pattern)
            # print("best_word", best_word)
            pattern_words[str(pattern)][ex_toString(best_word)] = get_tree(words_in_pattern, best_word)

    return pattern_words


def get_tree_better_freq(words, word, word_size=5):
    pattern_words = {}

    for pattern in combinations:
        words_in_pattern = update_current_words_2(words, list(pattern), word)
        if not words_in_pattern:
            continue

        if pattern == (2, 2, 2, 2, 2):
            pattern_words[str((2, 2, 2, 2, 2))] = True
            continue

        pattern_words[str(pattern)] = {}

        if len(words_in_pattern) == 1:
            temp_dict = {}
            temp_dict[str((2, 2, 2, 2, 2))] = True
            pattern_words[str(pattern)][ex_toString(words_in_pattern[0])] = temp_dict
        else:
            # pattern_words[str(pattern)][ex_toString(words_in_pattern[0])] = get_tree_better_freq(words_in_pattern, pick_better_freq(words_in_pattern))
            best_word = pick_better_freq(words_in_pattern)
            pattern_words[str(pattern)][ex_toString(best_word)] = get_tree_better_freq(words_in_pattern, best_word)

    return pattern_words


# def save_get_tree(words, word_start):
#     res = get_tree(words, word_start)
#     word_trees = {ex_toString(word_start): res}
#     with open("" + json_word_trees, 'w') as outfile:
#         json.dump(word_trees, outfile, indent=5)

def save_get_tree_better_freq(words, word_start):
    res2 = get_tree_better_freq(words, word_start)
    word_trees_2 = {ex_toString(word_start): res2}
    with open("better_freq_" + json_word_trees, 'w') as outfile:
        json.dump(word_trees_2, outfile, indent=5)


def save_min_average(words, word_start):
    res2 = get_tree_min_average(words, word_start)
    word_trees_1 = {ex_toString(word_start): res2}
    with open("min_average_" + json_word_trees, 'w') as outfile:
        json.dump(word_trees_1, outfile, indent=5)


def save_trees():
    words = get_game_words()[:]
    word_start = pick_better_freq(words)
    # save_get_tree(words, word_start)
    # print("Enthropy tree completed")
    save_min_average(words, word_start)
    print("Minimum average tree completed")
    save_get_tree_better_freq(words, word_start)
    print("Better freq tree completed")


def calculate_tree_guesses(tree_dict, count=1):
    if tree_dict is True:
        return count

    sum_guesses = 0
    num_guesses = 0

    word = list(tree_dict.keys())[0]
    patterns = tree_dict[word]

    for pattern in patterns:
        temp_count = calculate_tree_guesses(tree_dict[word][pattern], count=count + 1)
        sum_guesses += temp_count
        num_guesses += 1

    return sum_guesses / num_guesses


def calculate_trees_average():
    # with open("ALLWORDS_"+json_word_trees, "r") as infile:
    #     data = json.load(infile)
    #     enthropy_tree = calculate_tree_guesses(data)
    # with open("ALLWORDS_better_freq_" + json_word_trees, 'r') as infile:
    #     data = json.load(infile)
    #     better_freq_tree = calculate_tree_guesses(data)
    #
    # print("ENTHROPY TREE (ALL WORDS):", enthropy_tree)
    # print("BETTER FREQ TREE (ALL WORDS):", better_freq_tree)

    # with open(json_word_trees, "r") as infile:
    #     data = json.load(infile)
    #     enthropy_tree = calculate_tree_guesses(data)
    with open("better_freq_" + json_word_trees, 'r') as infile:
        data = json.load(infile)
        better_freq_tree = calculate_tree_guesses(data)

    # print("ENTHROPY TREE:", enthropy_tree)
    print("BETTER FREQ TREE:", better_freq_tree)


# calc_time(save_trees)
# calc_time(calculate_trees_average)

# wl = [['m', 'e', 'n', 't', 'a'], ['ż', 'e', 'n', 't', 'a'], ['p', 'o', 'n', 't', 'a'], ['t', 'a', 'n', 't', 'x']]
# res = get_enthropy(wl, expand_word("żenta"))
# print(res)
