@cuda.jit
def test(word_list, best_word):
    # numba.cuda.local.array(4, int)

    # xx, x, y = cuda.grid(3)
    # if xx < an_array.shape[0] and x < an_array.shape[0] and y < an_array.shape[1]:
    #     an_array[x, y] = 456

    ALPHABET_length = 30
    letter_freq_pos = cuda.local.array((5, ALPHABET_length), dtype=np.uint8)
    letter_freq = cuda.local.array((ALPHABET_length,), dtype=np.uint8)

    word_id = cuda.grid(1)
    if word_id < word_list.shape[0]:
        letter_id = cuda.grid(1)
        if letter_id < word_list.shape[1]:
            letter = word_list[word_id][letter_id]
            letter_freq_pos[letter_id][letter] += 1
            letter_freq[letter] += 1

    best_score = 0
    word_id = cuda.grid(1)
    if word_id < word_list.shape[0]:
        # Setting to 0
        seen_alphabet = cuda.local.array((ALPHABET_length,), dtype=np.uint8)
        seen_alphabet_id = cuda.grid(1)
        if seen_alphabet_id < seen_alphabet.shape[0]:
            seen_alphabet[seen_alphabet_id] = 0

        rating = 0

        letter_id = cuda.grid(1)
        if letter_id < word_list.shape[1]:
            letter = word_list[word_id][letter_id]
            if seen_alphabet[letter_id] != 1:  # If not seen
                seen_alphabet[letter_id] = 1  # Set to seen
                rating += letter_freq[letter]
                rating += letter_freq_pos[letter_id][letter] * 3

                if rating > best_score:
                    best_score = rating
                    best_word_id = cuda.grid(1)
                    if best_word_id < best_word.shape[0]:
                        best_word[best_word_id] = word_list[word_id][best_word_id]

        # def pick_freq(word_list):
        #     word_length = 5
        #     # player_words = word_list
        #     # Getting all letter frequencies
        #
        #     letter_freq_pos = np.zeros((word_length, len(ALPHABET)),
        #                                dtype=int)  # List of frequencies with the letter in that particular position
        #     letter_freq = np.zeros(len(ALPHABET), dtype=int)  # List of frequencies for letter in general
        #     for word in word_list:
        #         for i in range(len(word)):
        #             letter = word[i]
        #             letter_freq_pos[i][ALPHABET.index(letter)] += 1
        #             letter_freq[ALPHABET.index(letter)] += 1
        #     letter_freq_pos = letter_freq_pos  # ???
        #     letter_freq = letter_freq  # ???
        #
        #     # Getting ratings of all words
        #     best_score = 0
        #     best_word = []
        #     for word in word_list:
        #         word_unique = np.unique(word)
        #
        #         rating = 0
        #         for i in range(len(word_unique)):
        #             letter = word_unique[i]
        #             rating += letter_freq[ALPHABET.index(letter)]
        #             rating += letter_freq_pos[i][ALPHABET.index(letter)] * 3
        #
        #             if rating > best_score:
        #                 best_score = rating
        #                 best_word = word
        #
        #     return best_word


def convert():
    global words
    global ALPHABET

    new_words = []
    for word in words:
        w = []
        for letter in word:
            w.append(ALPHABET.index(letter))
        new_words.append(w)
    words = new_words

    # new_al = []
    # for i in range(len(ALPHABET)):
    #     new_al.append(i)
    # ALPHABET = new_al


convert()



if __name__ == "__main__":
    start = time.time()
    # d_ary = words
    all_words = cuda.to_device(words)
    best_word = cuda.to_device(np.array([-1, -1, -1, -1, -1]))
    # ALPHABET = cuda.to_device(ALPHABET)
    # print(d_ary, d_ary.shape)

    threadsperblock = (32, 32)
    blockspergrid_x = math.ceil(all_words.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(all_words.shape[1] / threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_x, blockspergrid_y)

    # Creating variables
    for i in range(10):
        test[blockspergrid, threadsperblock](all_words, best_word)
    print(ALPHABET[best_word[0]], ALPHABET[best_word[1]], ALPHABET[best_word[2]], ALPHABET[best_word[3]], ALPHABET[best_word[4]])
    # print(d_ary[2, 0])
    # print(words[0])

    end = time.time() - start
    print(end)

    w2 = get_words()
    start = time.time()
    # for xx in words:
    #     for x in words:
    #         for y in x:
    #             pass
    for i in range(10):
        res = pick_freq(w2)
    print(res)
    end = time.time() - start
    print(end)

def getTreeExplore(word_list, word, round=0, found_letters=None, letters_in=None):
    if letters_in is None:
        letters_in = set()
    if found_letters is None:
        found_letters = set()

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
            # best_word = pickerFunction(words_in_pattern)

            if len(letters_in) <= 4 and round <= 3:
                best_word = explore_pick(words_in_pattern, found_letters)
            else:
                best_word = pick_freq(words_in_pattern)

            temp_found_letters = copy.deepcopy(found_letters)
            temp_letterns_in = copy.deepcopy(letters_in)

            # Updating found_letters and letters_in
            for i in range(len(pattern)):
                if pattern[i] == Mark.PERFECT or pattern[i] == Mark.GOOD:  # Adding met letters that are correct
                    if word[i] not in temp_letterns_in:
                        temp_letterns_in.add(word[i])
                if word[i] not in temp_found_letters:  # Adding all letters encountered
                    temp_found_letters.add(word[i])

            # print(temp_found_letters, temp_letterns_in, words_in_pattern, pattern, word, best_word)
            pattern_words[str(tuple(pattern))][ex_toString(best_word)] = getTreeExplore(words_in_pattern, best_word, round=round+1, found_letters=temp_found_letters, letters_in=temp_letterns_in)

    return pattern_words


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
    if len(word_list_temp) != 0:
        # picked_word = pick_better_freq(word_list_temp)
        letter_freq_pos, letter_freq = get_freq_letters(word_list)
        picked_word = pick_freq(word_list_temp, letter_freq_pos, letter_freq)
        # print("PICKED WORD", picked_word)
    else:
        picked_word = pick_freq(word_list)
    # print("PICKED WORD", picked_word)

    return picked_word

def fullExporePick(word_list, num_letter_occurrence, concluded, avaliable_letters):
    word_list_temp = []
    lowest_count = math.inf
    best_unique_count = 0

    for word in all_words:
        # Gets number of letters that are already concluded
        count_letters = 0
        for i in range(len(word)):
            letter = word[i]
            if letter in concluded:
                count_letters += 1
            elif letter in num_letter_occurrence:
                if num_letter_occurrence[letter] >= word.count(letter):
                    count_letters += 1
            elif len(avaliable_letters[i]) == 0 and avaliable_letters[i] == letter:
                count_letters += 1

        unique_letters = len(np.unique(word))
        if count_letters < lowest_count:  # Minimising letters already concluded
            lowest_count = count_letters
            best_unique_count = unique_letters
            word_list_temp.clear()
            word_list_temp.append(word)
        elif count_letters == lowest_count and unique_letters > best_unique_count:  # Maximising unique letters
            best_unique_count = unique_letters
            word_list_temp.clear()
            word_list_temp.append(word)
        elif count_letters == lowest_count:  # and unique_letters == best_unique_count:  # Keeping a pool of equally good words
            word_list_temp.append(word)

    if len(word_list_temp) > 0:
        # picked_word = pick_better_freq(word_list_temp)
        letter_freq_pos, letter_freq = get_freq_letters(word_list)
        picked_word = pick_better_freq2(word_list_temp, letter_freq_pos, letter_freq)
        # print("PICKED WORD", picked_word)
    else:
        picked_word = pick_better_freq(word_list)

    return picked_word

# Update thing in explore
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
        num_letter_occurrence_pretemp = {}  # Number of occurrences

        for i in range(len(pattern)):
            letter = word[i]
            # for j in range(len(marking)):
            if pattern[i] == Mark.GOOD or pattern[i] == Mark.PERFECT:  # If marked with good, add the number
                num_letter_occurrence_pretemp[letter] = 1 if letter not in num_letter_occurrence_pretemp else \
                    num_letter_occurrence_pretemp[letter] + 1
            elif pattern[i] == Mark.BLANK:  # Whenever a blank is encountered, then number of letters is concluded
                if letter not in concluded_temp:
                    concluded_temp.append(letter)
# END

# design the neural network model
model = Sequential()
model.add(Dense(10, input_dim=PARAM_SIZE, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(10, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(1))
# define the loss function and optimization algorithm
model.compile(loss='mse', optimizer='adam')

episodes_num = 1
for i in range(episodes_num):
    param = randomParameters()
    # result = playBetterFrequencyFull(parameters=(expandParameters(param)))
    # reward = result.win_rate
    reward = np.asarray([0.9])
    # param = tf.convert_to_tensor(param, dtype=tf.float16)
    param = np.reshape(param, (1, PARAM_SIZE))
    model.fit(param, reward, batch_size=10, epochs=100, verbose=0)  # , batch_size=10
    check = model.predict(param)
    print(check)

tes = model.Maximum()
print(tes)