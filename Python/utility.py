import numpy as np
import pickle
import time
import json

ALPHABET = ['a', 'b', 'ċ', 'd', 'e', 'f', 'ġ', 'g', 'għ', 'h', 'ħ', 'i', 'ie', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'ż', 'z']
ALPHABET_BAD = ['a', 'b', 'ċ', 'd', 'e', 'f', 'ġ', 'g', 'h', 'ħ', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                'r', 's', 't', 'u', 'v', 'w', 'x', 'ż', 'z']


def calc_time(function):
    print("START")
    start = time.time()
    function()
    time_taken = time.time() - start
    name = function.__name__
    print("Time taken for function \'" + name + "\'\tSeconds:", time_taken, "\tMinutes:", time_taken / 60, "\tHours:",
          time_taken / 3600)


# def get_game_words():
#     words = []
#     freq = get_frequency()
#     for word, f in freq.items():
#         if f > 500:
#             words.append(expand_word(word))
#     # words = list(get_frequency().keys())
#
#     return words


# def get_player_words():
#     words = []
#     freq = get_frequency()
#     for word, f in freq.items():
#         if f > 1:
#             words.append(expand_word(word))
#
#     return words

def get_words():
    words = []
    freq = get_frequency()
    for word, f in freq.items():
        if f > 1:
            words.append(expand_word(word))

    return words[:]


def getWordsHash(words=None):
    if not words:
        words = get_words()
    word_hash = {ex_toString(words[i]): np.uint16(i) for i in range(len(words))}
    return word_hash


def get_frequency(file=True):
    file = open('frequency.pkl', 'rb')
    data = pickle.load(file)

    if filter:
        data = {key: cnt for key, cnt in data.items() if cnt > 1}

    return data


# def get_words_rated():
#     file = open('words_rated.pkl', 'rb')
#     data = pickle.load(file)
#
#     return data


def expand_word(word):
    ex_word = []

    counter = 0
    i = 0
    while i < len(word):
        letter = word[i]

        if i < len(word) - 1:
            if word[i] == "i" and word[i + 1] == 'e':
                letter = "ie"
                i += 1
            if word[i] == "g" and word[i + 1] == "ħ":
                letter = "għ"
                i += 1

        ex_word.append(letter)

        counter += 1
        i += 1

    return ex_word


def expand_word_BAD(word):
    ex_word = list(word)

    return ex_word


def ex_toString(word_list):
    word = ""
    for x in word_list:
        word += x
    return word


def softmax(arr):
    max = np.sum(arr)
    return arr / max


def get_letter_frequency(word_list, word_length=5):
    num_words = len(word_list)

    # Getting frequency of letters
    letter_freq_pos = np.zeros((len(ALPHABET), word_length),
                               dtype=int)  # List of frequencies with the letter in that particular position
    for word in word_list:
        for i in range(len(word)):
            letter = word[i]
            letter_freq_pos[ALPHABET.index(letter)][i] += 1
    # print(letter_freq_pos)

    return letter_freq_pos


class Pattern:
    def __init__(self):
        self.base = 3
        self.pattern_len = 5
        # self.max_pattern = self.base **

    def encodePattern(self, lst):
        code = 0
        for i in range(len(lst)):
            code += lst[i] * self.base ** i
        return np.uint8(code)

    def decodePattern(self, code):
        lst = []
        for i in range(self.pattern_len):
            lst.append(code % self.base)
            code = code // self.base
        return lst

    def __dict__(self, default_value=None):
        pattern_dict = {self.encodePattern(pattern): default_value for pattern in self}
        return pattern_dict

    def __iter__(self):
        for i in range(len(self)):
            yield self.decodePattern(i)

    def __len__(self):
        return self.base ** self.pattern_len

    def __getitem__(self, code):
        return self.decodePattern(code)

    def toList(self):
        lst = []
        for pattern in self:
            lst.append(pattern)
        return lst

def loadFile(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
        return data


def saveFile(path, object):
    with open(path, "wb") as f:
        pickle.dump(object, f)


def saveJson(path, object, indent=6):
    with open(path, 'w') as outfile:
        json.dump(object, outfile, indent=indent)


def loadJson(path):
    with open(path, "r") as infile:
        data = json.load(infile)
        return data
