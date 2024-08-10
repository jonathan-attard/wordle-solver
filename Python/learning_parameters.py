import pprint

from wordle import *
from tqdm import tqdm
import itertools
from multiprocessing import Pool
import csv
from os.path import exists

patterns = Pattern()


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

    avaliable_letters = [[] for i in range(patterns.pattern_len)]

    for i in range(len(pattern)):
        if pattern[i] == Mark.GOOD:
            temp_alph = copy.deepcopy(ALPHABET)
            temp_alph.remove(word[i])
            avaliable_letters[i] = temp_alph
        elif pattern[i] == Mark.PERFECT:
            avaliable_letters[i] = [word[i]]

    return num_letter_occurrence, concluded, avaliable_letters


def pick_freq(word_list, letter_freq_pos=None, letter_freq=None, parameters=None):
    if letter_freq is None and letter_freq_pos is None:
        (letter_freq, letter_freq_pos) = get_freq_pos(word_list)

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


def fullExporePick(word_list, num_letter_occurrence, concluded, available_letters, letter_freq, letter_freq_pos,
                   all_words=None, strength_params=None):
    if all_words is None:
        all_words = word_list

    word_length = 5

    # print(strength_params)

    if strength_params is None:
        strength_freq = 0           # 0.5
        strength_letter_pos = 0     # 0
        strength_concluded = 0      # 0.5
        strength_occur = 0          # 0
        strength_perfect = 0        # 0.5
        strength_available = 0      # 0
    else:
        (strength_freq,
         strength_letter_pos,
         strength_concluded,
         strength_occur,
         strength_perfect,
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
            if len(available_letters[i]) == 0 and available_letters[i][0] == letter:
                rating -= (1 / word_length) * strength_perfect
            if letter in available_letters[i] and len(available_letters[i]) != 0:
                rating += (1 / word_length) * strength_available

        if rating > best_score:
            best_score = rating
            best_word = word

    # print(best_word, word_list, letter_freq_pos, letter_freq)
    if len(best_word) == 0:
        best_word = word_list[0]

    return best_word


# IMPORTANT REVISIT THIS!
def calculate_tree_guesses(tree_dict, wr, count=0):
    if tree_dict is True:
        if count > 5:  # Was 5
            wr.addLoss()
        else:
            wr.addWin()
        return count

    sum_guesses = 0
    num_guesses = 0

    word = list(tree_dict.keys())[0]

    if tree_dict[word] is False:  # Finished early, game lost
        wr.addLoss()
        return 0

    patterns = tree_dict[word]

    for pattern in patterns:
        temp_count = calculate_tree_guesses(tree_dict[word][pattern], wr, count=count + 1)
        sum_guesses += temp_count
        num_guesses += 1

    return sum_guesses / num_guesses


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
                num_letter_occurrence_temp = copy.deepcopy(num_letter_occurrence)
                concluded_temp = copy.deepcopy(concluded)  # We know the number of occurrences for a letter
                avaliable_letters_temp = copy.deepcopy(avaliable_letters)
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


class WinLoss:
    def __init__(self):
        self.wins = 0
        self.losses = 0

    def addWin(self):
        self.wins += 1

    def addLoss(self):
        self.losses += 1

    def getWinRate(self):
        if (self.wins + self.losses) == 0:
            return 0
        return self.wins / (self.wins + self.losses)


class TreeResults:
    def __init__(self, average_guess=None, win_rate=None, parameters=None, csv_title="tree_parameters.csv", show_number=True):
        self.average_guess = average_guess
        self.win_rate = win_rate
        self.parameters = parameters

        # Creating CSV
        self.csv_title = csv_title
        self.show_number = show_number
        if not exists(self.csv_title):
            fields = ['Average Guess', 'Win Ratio', 'Parameters']
            if self.show_number:
                fields = ['Number of words', 'Average Guess', 'Win Ratio', 'Parameters']
            with open(self.csv_title, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(fields)

    def __repr__(self):
        return "Average guess: " + str(self.average_guess) + "\t\tWin ratio: " + str(
            self.win_rate) + "\t\tParameters:" + str(self.parameters)

    def writeCSV(self):
        with open(self.csv_title, 'a', newline='') as f:
            writer = csv.writer(f)
            if self.show_number:
                to_write = [len(words), self.average_guess, self.win_rate, self.parameters]
            else:
                to_write = [self.average_guess, self.win_rate, self.parameters]
            writer.writerow(to_write)


words = get_words()
start_word = pick_freq(words)


# Creates and evaluates tree
def playBetterFrequencyFull(parameters=None, save=True):
    # parameters = (0.5, 0, 0.5, 0, 0.5, 0)  # Found to be the best
    # NEW!! (0.6, 0.2, 0.6, 0, 0, 0)
    res = {ex_toString(start_word): getTreeExploreFull(words, start_word, parameters=parameters)}
    if save:
        saveJson("SolverLast.json", res)
    # pprint.pprint((res))

    wr = WinLoss()
    avg_g = calculate_tree_guesses(res, wr)
    tree_result = TreeResults(average_guess=avg_g, win_rate=wr.getWinRate(), parameters=parameters)
    print(tree_result)
    tree_result.writeCSV()

    return tree_result


result = playBetterFrequencyFull(parameters=(0.5, 0, 0.5, 0, 0.5, 0))
print(result)

# Main method
# if __name__ == '__main__':
#     exit()
#
#     num_diff = [0, 0.2, 0.4, 0.6]
#     num_parameters = 6
#
#     parameter_combo = itertools.product(num_diff, num_diff, num_diff, num_diff, num_diff, num_diff)
#     # parameter_combo = [(0.5, 0, 0.5, 0, 0, 0), (0.5, 0, 0.5, 0, 0.5, 0), (1, 0, 1, 0, 0.5, 0)]
#
#     pool = Pool(processes=6)  # use all available cores, otherwise specify the number you want as an argument
#     for parameter in parameter_combo:
#         pool.apply_async(playBetterFrequencyFull, args=(parameter,))
#
#     pool.close()
#     pool.join()

