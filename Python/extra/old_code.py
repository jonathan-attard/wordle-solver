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


def get_word_scores(word_list, word_length=5):
    word_scores = {}
    max_freq = [0] * word_length

    letter_freq_pos = get_letter_frequency(word_list, word_length)

    for i in range(len(letter_freq_pos)):
        for j in range(word_length):
            if max_freq[j] < letter_freq_pos[i][j]:
                max_freq[j] = letter_freq_pos[i][j]
    for word in word_list:
        score = 1
        for i in range(word_length):
            letter = word[i]
            score *= 1 + (letter_freq_pos[ALPHABET.index(letter)][i] - max_freq[i]) ** 2
        word_scores[ex_toString(word)] = score
        score += np.random.uniform(0, 1)
    return word_scores


def get_best(word_list, word_length=5):
    max_score = 100000000000000000000
    best_word = []
    scores = get_word_scores(word_list, word_length)
    for word in word_list:
        if scores[ex_toString(word)] < max_score:
            max_score = scores[ex_toString(word)]
            best_word = word
    return best_word

# res = get_best(get_words())
# print(res)