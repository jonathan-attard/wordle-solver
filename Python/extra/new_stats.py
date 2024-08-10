import copy

from wordle import *


def update_current_words_2_number(word_list, marking, guess_word):
    # print(marking, guess_word)
    number_removed = 0

    num_letter_occurance = {}  # Number of occurances
    unique_letters = np.unique(guess_word)
    concluded = []  # We know the number of occurances for a letter
    # Check if there is a case where a letter has 'good' and another 'blank'
    for i in range(len(marking)):
        letter = guess_word[i]
        # for j in range(len(marking)):
        if marking[i] == Mark.GOOD or marking[i] == Mark.PERFECT:  # If marked with good, add the number
            if letter not in num_letter_occurance:
                num_letter_occurance[letter] = 1
            elif letter in num_letter_occurance:
                num_letter_occurance[letter] += 1
        elif marking[i] == Mark.BLANK:
            if letter not in concluded:
                concluded.append(letter)

    for word in word_list:
        keep = True

        # Handels Mark.GOOD
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
                    if c in num_letter_occurance:  # If concluded with number, check for that count number
                        if word.count(c) != num_letter_occurance[c]:
                            keep = False
                            break
                    else:  # If concluded with no number, therefore count was equal to 0
                        if word.count(c) != 0:
                            keep = False
                            break
                else:  # If unconcluded, make sure that number stays above which was found
                    if c in num_letter_occurance:
                        if word.count(c) < num_letter_occurance[c]:
                            keep = False
                            break

        # Handels Mark.PERFECT
        if keep:
            for i in range(len(marking)):
                if marking[i] == Mark.PERFECT:
                    if guess_word[i] != word[i]:
                        keep = False
                        # print("REMOVED4", word)
                        break

        # Finally appending to list
        if not keep:
            number_removed += 1

    return number_removed

from tqdm import tqdm
def new_stats_word_combinations():
    # global all_words
    # all_words = all_words[:1000]
    all_words = get_frequency()

    count = len(all_words)
    sum = np.zeros(len(all_words), dtype=float)
    pbar2 = tqdm(total=len(all_words))
    for word_chosen in all_words:
        word_chosen = expand_word(word_chosen)
        pbar2.update(1)
        # pbar = tqdm(total=len(all_words))

        # print(all_words.index(word_chosen) / len(all_words), "complete\n")
        for word_guess in all_words:
            word_guess = expand_word(word_guess)
            # pbar.update(1)
            if word_guess == word_chosen:
                continue

            w = Wordle(chosen_word=word_chosen)
            markings, done = w.guess(word_guess)

            number_removed = update_current_words_2_number(all_words, markings, word_guess)

            res = number_removed / len(all_words)
            # print(len(all_words), len(temp_all_words))
            # print("CHOSEN:", word_chosen, "\t\tGUESS:", word_guess, "\t\tperc_removed:", res)
            sum[list(all_words).index(ex_toString(word_guess))] += res
        # pbar.close()
    pbar2.close()
    sum /= len(all_words)
    print(sum)
    out = open("breadth_search2.pkl", "wb")
    pickle.dump(sum, out)

# new_stats_word_combinations()

import itertools
def give_rating_to_pattern():
    type_number = 3
    word_size = 5
    combinations = [x for x in itertools.product(range(type_number),
                                                    repeat=word_size)]  # https://www.daniweb.com/programming/software-development/threads/435159/n-number-for-nested-for-loops
    print(combinations)

    count = len(combinations)
    sum_rating = np.zeros(len(all_words), dtype=float)

    for word in all_words:
        score = 0
        for pattern in combinations:

            removed_num = update_current_words_2_number(all_words, list(pattern), word)

            res = removed_num / len(all_words)

            score += res
        sum_rating[all_words.index(word)] = score/count
        print("Rating of word", word, "is", sum_rating[all_words.index(word)])
# give_rating_to_pattern()

