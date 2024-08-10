# visuals = False
visuals = True

import copy

import numpy as np

from utility import *

# from stats import *
if visuals:
    from game_utils import show_game, resetGrid
import random

all_words = get_words()
frequency_words = get_frequency()


# print("Number of words:", len(all_words))#, print(dict(sorted(frequency_words.items(), key=lambda item: item[1], reverse=True))))


class Mark:
    BLANK = 0
    GOOD = 1
    PERFECT = 2


class Wordle:
    max_round = 6
    word_size = 5

    chosen_word = ""
    round = 0

    history_words = []
    history_marking = []

    def __init__(self, max_round=6, word_size=5, chosen_word=None):
        self.max_round = max_round
        self.word_size = word_size

        if chosen_word is None:
            chosen_word = random.choice(all_words)  # random.choices(all_words, weights=frequency_words, k=1)[0]
        self.chosen_word = chosen_word

        self.history_words.clear()
        self.history_marking.clear()
        round = 0

        if visuals:
            resetGrid()

        # print("W O R D:\t", self.chosen_word)

    def guess(self, word):

        done = False
        marking = np.zeros(self.word_size)

        if word == self.chosen_word:
            done = True

        freq_letters_in_chosen = {x: self.chosen_word.count(x) for x in self.chosen_word}

        # First check prefects
        # print(self.chosen_word, word)
        for i in range(len(word)):
            letter = word[i]
            if letter == self.chosen_word[i]:
                marking[i] = Mark.PERFECT
                freq_letters_in_chosen[letter] -= 1

        # Then check good letter (not in position)
        for i in range(len(word)):
            letter = word[i]
            if letter in self.chosen_word:
                if marking[i] == Mark.BLANK:
                    if freq_letters_in_chosen[letter] > 0:
                        marking[i] = Mark.GOOD
                        freq_letters_in_chosen[letter] -= 1

        self.history_words.append(word)
        self.history_marking.append(marking)
        self.round += 1

        # Apply pygame
        # print(ex_toString(self.chosen_word))
        # print(self.history_words)
        if visuals:
            show_game(self.history_words, self.history_marking, ex_toString(self.chosen_word))

        return marking, done


def update_current_words(word_list, marking, word):
    word_list.remove(word)  # Removing non-matching word

    for i in range(len(marking)):
        all_words_temp2 = copy.deepcopy(word_list)
        if marking[i] == Mark.PERFECT:
            for word_ in all_words_temp2:
                if word[i] != word_[i]:
                    word_list.remove(word_)
                    # print("REMOVED2", word_)

    # Get number of good letters (not in position)
    num_letter_occurance = {}  # Number of occurances
    unique_letters = np.unique(word)
    concluded = []  # We know the number of occurances for a letter
    # Check if there is a case where a letter has 'good' and another 'blank'
    for i in range(len(marking)):
        letter = word[i]
        # for j in range(len(marking)):
        if marking[i] == Mark.GOOD or marking[i] == Mark.PERFECT:  # If marked with good, add the number
            if letter not in num_letter_occurance:
                num_letter_occurance[letter] = 1
            elif letter in num_letter_occurance:
                num_letter_occurance[letter] += 1
        elif marking[i] == Mark.BLANK:
            if letter not in concluded:
                concluded.append(letter)
    # print(word)
    # print(num_letter_occurance)
    # print(concluded)

    # Applying concluded
    for c in unique_letters:
        all_words_temp2 = copy.deepcopy(word_list)
        for word_ in all_words_temp2:
            if c in concluded:
                if c in num_letter_occurance:
                    if word_.count(c) != num_letter_occurance[c]:
                        word_list.remove(word_)
                else:
                    if word_.count(c) != 0:
                        word_list.remove(word_)
            else:
                if c in num_letter_occurance:
                    if word_.count(c) < num_letter_occurance[c]:
                        word_list.remove(word_)

    return word_list


def update_current_words_2(word_list, marking, guess_word, more_return=False):
    # print(marking, guess_word)
    word_list_temp = []

    num_letter_occurrence = {}  # Number of occurrences
    unique_letters = np.unique(guess_word)
    concluded = []  # We know the number of occurrences for a letter
    # Check if there is a case where a letter has 'good' and another 'blank'
    for i in range(len(marking)):
        letter = guess_word[i]
        # for j in range(len(marking)):
        if marking[i] == Mark.GOOD or marking[i] == Mark.PERFECT:  # If marked with good, add the number
            if letter not in num_letter_occurrence:
                num_letter_occurrence[letter] = 1
            elif letter in num_letter_occurrence:
                num_letter_occurrence[letter] += 1
        elif marking[i] == Mark.BLANK:
            if letter not in concluded:
                concluded.append(letter)

    for word in word_list:
        keep = True

        # Handles Mark.GOOD
        if keep:
            for i in range(len(marking)):
                if marking[i] == Mark.GOOD:
                    if guess_word[i] not in word:  # If a good letter isn't within the word, remove it
                        keep = False
                        # print("REMOVED1", word)
                        break
                    elif guess_word[i] == word[i]:  # If good letter is in but in the exact position, remove it
                        keep = False
                        # print("REMOVED2", word)
                        break

        # Applying concluded letter numbers (includes handling of MArk.BLANK)
        if keep:
            for c in unique_letters:
                if c in concluded:  # Check all concluded letters first
                    if c in num_letter_occurrence:  # If concluded with number, check for that count number
                        if word.count(c) != num_letter_occurrence[c]:
                            keep = False
                            break
                    else:  # If concluded with no number, therefore count was equal to 0
                        if word.count(c) != 0:
                            keep = False
                            break
                else:  # If unconcluded, make sure that number stays above which was found
                    if c in num_letter_occurrence:
                        if word.count(c) < num_letter_occurrence[c]:
                            keep = False
                            break

        # Handles Mark.PERFECT
        if keep:
            for i in range(len(marking)):
                if marking[i] == Mark.PERFECT:
                    if guess_word[i] != word[i]:
                        keep = False
                        break

        # Finally, appending to list
        if keep:
            word_list_temp.append(word)

    if more_return:
        return word_list_temp, num_letter_occurrence, concluded

    return word_list_temp


def update_current_words_len(word_list, marking, guess_word):
    # print(marking, guess_word)
    count = 0

    num_letter_occurrence = {}  # Number of occurrences
    unique_letters = np.unique(guess_word)
    concluded = []  # We know the number of occurrences for a letter
    # Check if there is a case where a letter has 'good' and another 'blank'
    for i in range(len(marking)):
        letter = guess_word[i]
        # for j in range(len(marking)):
        if marking[i] == Mark.GOOD or marking[i] == Mark.PERFECT:  # If marked with good, add the number
            if letter not in num_letter_occurrence:
                num_letter_occurrence[letter] = 1
            elif letter in num_letter_occurrence:
                num_letter_occurrence[letter] += 1
        elif marking[i] == Mark.BLANK:
            if letter not in concluded:
                concluded.append(letter)

    for word in word_list:
        keep = True

        # Handles Mark.GOOD
        if keep:
            for i in range(len(marking)):
                if marking[i] == Mark.GOOD:
                    if guess_word[i] not in word:  # If a good letter isn't within the word, remove it
                        keep = False
                        # print("REMOVED1", word)
                        break
                    elif guess_word[i] == word[i]:  # If good letter is in but in the exact position, remove it
                        keep = False
                        # print("REMOVED2", word)
                        break

        # Applying concluded letter numbers (includes handling of MArk.BLANK)
        if keep:
            for c in unique_letters:
                if c in concluded:  # Check all concluded letters first
                    if c in num_letter_occurrence:  # If concluded with number, check for that count number
                        if word.count(c) != num_letter_occurrence[c]:
                            keep = False
                            break
                    else:  # If concluded with no number, therefore count was equal to 0
                        if word.count(c) != 0:
                            keep = False
                            break
                else:  # If unconcluded, make sure that number stays above which was found
                    if c in num_letter_occurrence:
                        if word.count(c) < num_letter_occurrence[c]:
                            keep = False
                            break

        # Handles Mark.PERFECT
        if keep:
            for i in range(len(marking)):
                if marking[i] == Mark.PERFECT:
                    if guess_word[i] != word[i]:
                        keep = False
                        break

        # Finally, appending to list
        if keep:
            count += 1

    return count

# w = Wordle(chosen_word=expand_word("ponta"))
# print(w.guess(expand_word("umani")))
# guess = expand_word("tantx")
# m, d = w.guess(guess)
# print(m, d)
# print(update_current_words_2(get_game_words(), m, guess))
#
# for
