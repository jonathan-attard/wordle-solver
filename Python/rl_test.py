# https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
# https://github.com/moduIo/Deep-Q-network/blob/master/DQN.ipynb

import os

import numpy as np
from collections import deque

from matplotlib import pyplot as plt
from IPython.display import clear_output
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Conv2D, MaxPooling2D
from keras.optimizers import Adam
import tensorflow as tf
from wordle import *

# from utility import *

alphabets = {ALPHABET[i]: i for i in range(len(ALPHABET))}
STATE_SIZE_FULL = (6, len(ALPHABET) * 5 + 5 * 3)
STATE_SIZE_FULL_FLAT = 6 * (len(ALPHABET) * 5 + 5 * 3)
STATE_SIZE = (len(ALPHABET) * 5 + 5 * 3)
ACTION_SIZE = (len(ALPHABET) * 5)

GUESS_COST = -1
WIN_REWARD = 10


def oneHotWord(word: list):
    idxs = [alphabets[ch] for ch in word]
    one_hot = tf.one_hot(idxs, len(alphabets), dtype=tf.uint8)
    return one_hot


def oneHotPattern(pattern: list):
    one_hot = tf.one_hot(pattern, 3, dtype=tf.uint8)
    return one_hot


def getStateFull(w: Wordle, flat=True):
    # Initialize empty state
    full_history = np.zeros(STATE_SIZE_FULL, dtype=np.uint8)

    # print(w.history_words, w.history_marking)

    for i in range(len(w.history_words)):
        word_enc = oneHotWord(w.history_words[i])
        for j in range(len(word_enc)):
            for k in range(len(word_enc[j])):
                full_history[i][k + (len(ALPHABET) * j)] = word_enc[j][k]

    jump_pattern = len(ALPHABET) * 5

    for i in range(len(w.history_marking)):
        pattern_enc = oneHotPattern(w.history_marking[i])
        for j in range(len(pattern_enc)):
            for k in range(len(pattern_enc[j])):
                full_history[i][jump_pattern + k + (3 * j)] = pattern_enc[j][k]

    if flat:
        full_history = full_history.flatten()

    full_history = tf.convert_to_tensor(full_history, dtype=tf.uint8)
    return full_history


def getState(w: Wordle, flat=True):
    # Initialize empty state
    full_history = np.zeros(STATE_SIZE, dtype=np.uint8)

    # print(w.history_words, w.history_marking)

    if len(w.history_words) > 0:
        word_enc = oneHotWord(w.history_words[-1])
        for j in range(len(word_enc)):
            for k in range(len(word_enc[j])):
                full_history[k + (len(ALPHABET) * j)] = word_enc[j][k]

        jump_pattern = len(ALPHABET) * 5

        pattern_enc = oneHotPattern(w.history_marking[-1])
        for j in range(len(pattern_enc)):
            for k in range(len(pattern_enc[j])):
                full_history[jump_pattern + k + (3 * j)] = pattern_enc[j][k]

    full_history = tf.convert_to_tensor(full_history, dtype=tf.uint8)
    return full_history


def getAction(word: list):
    # Initialize empty state
    act = np.zeros(ACTION_SIZE, dtype=np.uint8)

    word_enc = oneHotWord(word)

    for j in range(len(word_enc)):
        for k in range(len(word_enc[j])):
            act[k + (len(ALPHABET) * j)] = word_enc[j][k]

    act = tf.convert_to_tensor(act, dtype=tf.uint8)

    return act


def decodeAction(act):
    # act = act.numpy()
    act_temp = np.reshape(act, (5, len(ALPHABET)))

    word = []
    for letter in np.argmax(act_temp, axis=1):
        word.append(ALPHABET[letter])
    return word


def step(w: Wordle, action, full=False):
    marking, done = w.guess(action)

    reward = GUESS_COST
    reward += np.sum(marking)
    if done:
        reward += 100

    if full:
        return getStateFull(w), reward, done
    return getState(w), reward, done


def randomAction():
    chosen_word = random.choice(all_words)
    return chosen_word


class Callback(tf.keras.callbacks.Callback):
    SHOW_NUMBER = 10
    counter = 0
    epoch = 0

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch = epoch

    def on_train_batch_end(self, batch, logs=None):
        if self.counter == self.SHOW_NUMBER or self.epoch == 1:
            print('Epoch: ' + str(self.epoch) + ' loss: ' + str(logs['loss']))
            if self.epoch > 1:
                self.counter = 0
        self.counter += 1


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.learning_rate = 0.001
        self.model = self._build_model()

        self.my_memory = []
        self.alpha = 0.5

    def _build_model(self):
        model = keras.Sequential()
        model.add(keras.layers.Dense(32, activation="relu",
                                     input_dim=self.state_size))
        model.add(keras.layers.Dense(32, activation="relu"))
        model.add(keras.layers.Dense(self.action_size, activation="linear"))
        model.compile(loss="mse",
                      optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate), metrics=['accuracy'])

        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action,
                            reward, next_state, done))

    def train(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            if not done:
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)))
            else:
                target = reward

                # Construct the target vector as follows:
                # 1. Use the current model to output the Q-value predictions
            target_f = self.model.predict(state)

            # 2. Rewrite the chosen action value with the computed target
            target_f[0][action] = target

            # 3. Use vectors in the objective computation
            self.model.fit(state, target_f, epochs=10, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def my_train(self):
        state, action, reward, next_state, done = self.my_memory[-1]  # Last step (what will be updated)
        target = reward
        target_f = self.model.predict(state)
        target_f[0][action] = target
        self.model.fit(state, target_f, epochs=1, verbose=0)

        for i in range(len(self.my_memory) - 1):
            state_temp, action_temp, reward_temp, next_state_temp, done_temp = self.my_memory[i]

            target = reward

            target_f = self.model.predict(state_temp)
            target_f[0][action] = target

            self.model.fit(state_temp, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def my_remember(self, state, action, reward, next_state, done):
        self.my_memory.append((state, action,
                               reward, next_state, done))

    def my_remember_reset(self):
        self.my_memory.clear()

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return randomAction()
        act_values = decodeAction(self.model.predict(state))
        return act_values

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


def my_learning():
    agent = DQNAgent(STATE_SIZE_FULL_FLAT, ACTION_SIZE)
    batch_size = 32
    n_episodes = 1000
    output_dir = "model_output/wordle/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for e in range(n_episodes):
        w = Wordle()

        # state = getState(w)
        state = getStateFull(w)

        state = np.reshape(state, [1, STATE_SIZE_FULL_FLAT])
        total_reward = 0

        for guess_no in range(w.max_round):
            action = agent.act(state)
            next_state, reward, done = step(w, action, full=True)
            next_state = np.reshape(next_state, [1, STATE_SIZE_FULL_FLAT])
            inp_action = getAction(action)

            agent.my_remember(state, inp_action, reward, next_state, done)

            total_reward += reward

            agent.my_train()

            state = next_state

            if e % 50 == 0:
                agent.save(output_dir + "weights_"
                           + "{:04d}".format(e) + ".hdf5")

            if done:
                break
        print("episode: {}/{}, total_reward: {}, e: {:.2}"
              .format(e, n_episodes - 1, total_reward, agent.epsilon))
        agent.my_remember_reset()


def original_learning():  # Actually a bit edited (need to uncomment some things)
    agent = DQNAgent(STATE_SIZE, ACTION_SIZE)
    batch_size = 32
    n_episodes = 1000
    output_dir = "model_output/wordle/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for e in range(n_episodes):
        w = Wordle()

        state = getState(w)
        # state = getStateFull(w)

        state = np.reshape(state, [1, STATE_SIZE])
        total_reward = 0

        done = False
        time = 0
        for guess_no in range(w.max_round):
            action = agent.act(state)
            next_state, reward, done = step(w, action, full=False)  # Done does not stop if agent didnt win
            next_state = np.reshape(next_state, [1, STATE_SIZE])
            inp_action = getAction(action)

            agent.remember(state, inp_action, reward, next_state, done)

            total_reward += reward

            time += 1

            if len(agent.memory) > batch_size:
                agent.train(batch_size)
            # agent.my_train(state, inp_action, reward, next_state, done)

            state = next_state

            if e % 50 == 0:
                agent.save(output_dir + "weights_"
                           + "{:04d}".format(e) + ".hdf5")

            if done:
                break
        print("episode: {}/{}, score: {}, total_reward: {}, e: {:.2}"
              .format(e, n_episodes - 1, time, total_reward, agent.epsilon))


original_learning()
# my_learning()  # A very unique attempt
