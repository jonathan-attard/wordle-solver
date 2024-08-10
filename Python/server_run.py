from wordle import *
import itertools
import json

# This python script was run on the laptop server

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


combinations = [x for x in itertools.product(range(3),
                                             repeat=5)]  # https://www.daniweb.com/programming/software-development/threads/435159/n-number-for-nested-for-loops


# def

json_word_trees = "word_trees.json"  # {starting_word: {pattern1: {word1: {patterns}, word2: {patterns}}, pattern2: {word1: {patterns}, word2: {patterns}} }
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

all_words = all_words[:]
word_start = pick_better_freq(all_words)
res = get_patterns_and_words(all_words, word_start)
print("FINISHED")
word_trees = {}
word_trees[ex_toString(word_start)] = res
with open(json_word_trees, 'w') as outfile:
    json.dump(word_trees, outfile, indent=5)