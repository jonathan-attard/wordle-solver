# John J. Camilleri. "A Computational Grammar and Lexicon for Maltese", M.Sc. Thesis. Chalmers University of Technology. Gothenburg, Sweden, September 2013.
# Gatt, A., & Čéplö, S. (2013). Digital corpora and other electronic resources for Maltese. In Proceedings of the International Conference on Corpus Linguistics. Lancaster, UK: University of Lancaster.
import time

import bson
import pickle
import json
import os
from utility import *
import xml.etree.ElementTree as ET
from lxml import etree
import re
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


def old_corpus():
    game_words = get_game_words()
    words = []

    root_folder = "gabra/"

    f = open(root_folder + 'wordforms.bson', 'rb')
    data = bson.decode_iter(f.read())

    for d in data:
        if 'pending' in d:
            if d['pending']:
                continue
        if 'surface_form' not in d:
            continue

        show = d['surface_form'].lower()

        # Skip any non alphabet stuff
        skip = False
        for x in show:
            if x not in ALPHABET:
                skip = True
                break
        if skip:
            continue

        w = expand_word(show)

        if len(w) == 5:
            words.append(w)

    del data

    for w in game_words:
        if w not in words:
            words.append(w)

    print(words)
    out = open("wordsDICTIONARY.pkl", "wb")
    pickle.dump(words, out)

    words = {"wordsDICTIONARY": words}
    with open("wordsDICTIONARY.json", "w") as f:
        json.dump(words, f)


def new_corpus():
    # words = []
    frequency = {}

    root_folder = "corpus"

    for filename in os.scandir(root_folder):
        if filename.is_file():
            print(filename.path)

            f = open(filename.path, "r", encoding="utf-8")
            parser = etree.XMLParser(recover=True)
            xml = f.read()

            xml = "<root>" + xml + "</root>"

            root = ET.fromstring(xml, parser=parser)
            # tree = ET.tostring(root, encoding='utf8').decode('utf8')

            for e in root.iter('s'):
                text = e.text
                word_info = text.split("\n")
                for w in word_info:
                    word = w.split('\t')[0]
                    # print(word)

                    # word = word.lower()  # Setting word to lower case  Not doing it because of names

                    # Check word
                    skip = False
                    for x in word:
                        if x not in ALPHABET:
                            skip = True
                            break
                    if skip:
                        continue

                    word_inp = expand_word(word)

                    if word not in frequency:
                        if len(word_inp) == 5:
                            # words.append(word_inp)
                            frequency[word] = 1
                    else:
                        frequency[word] += 1

            f.close()

    frequency = dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True))

    print(frequency)
    out = open("frequency.pkl", "wb")
    pickle.dump(frequency, out)

    frequency = {"frequency": frequency}
    with open("frequency.json", "w") as f:
        json.dump(frequency, f)

# def extract_words():
#     saveJson("words.json", limited_frequency)

def getChartWordFrequencies():
    freq = get_frequency()
    df = pd.DataFrame(freq.values(), index=freq.keys(), columns=["Frequency"])
    # print(df)
    fig = px.bar(df)
    fig.show()

print(len(get_words()))
# calc_time(new_corpus)
# getChartWordFrequencies()
