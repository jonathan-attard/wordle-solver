import pickle
import random
import numpy as np
from utility import *

data = get_words()
# print(data)

num_words = len(data)

word_length = 5

# Getting frequency of letters
letter_freq_pos = np.zeros((word_length, len(ALPHABET)), dtype=int)  # List of frequencies with the letter in that particular position
letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
for word in data:
    for i in range(len(word)):
        letter = word[i]
        letter_freq_pos[i][ALPHABET.index(letter)] += 1
        letter_freq[ALPHABET.index(letter)] += 1
letter_freq_pos = letter_freq_pos / num_words
letter_freq = letter_freq / num_words

print(letter_freq_pos)

# Finding best word to start with
def print_lfp():
    while True:
        top_word = ""
        for lf in letter_freq_pos:
            max = np.argmax(lf)
            # print(lf)
            print("rating of:", lf[max])
            print("letter:", ALPHABET[max])
            top_word += ALPHABET[max]
        print("word:", top_word)

        break


def print_lf():
    letter_usage = []
    letter_freq_sorted = np.argsort(letter_freq)[::-1]
    for r in letter_freq_sorted:
        print("letter:", ALPHABET[r], "\trating:", letter_freq[r])

# print_lf()
# print_lfp()

def get_all_patterns(types, n, l=[]):
    if n >= 1:
        for i in range(types):
            l.append(i)
        get_all_patterns(types, n-1, l)
    else:
        return l


from wordle import *
def give_rating_to_word(bag_of_words):
    word_r = {}
    for word in bag_of_words:
        word_unique = np.unique(word)

        rating = 0
        for i in range(len(word_unique)):
            letter = word_unique[i]
            rating += letter_freq[ALPHABET.index(letter)]
            rating += letter_freq_pos[i][ALPHABET.index(letter)] * 3

        word_r[ex_toString(word)] = rating

    word_r = dict(sorted(word_r.items(), key=lambda item: item[1], reverse=True))

    print(word_r)
    out = open("words_rated.pkl", "wb")
    pickle.dump(word_r, out)

# new_data = update_current_words(data, [0, 0, 0, 0, 0], expand_word('unita'))
give_rating_to_word(data)
