import spacy
import streamlit as st
import csv
from functions import removeConsecutiveDuplicates
import nltk
from nltk.corpus import words
from nltk.tokenize import word_tokenize
from collections.abc import Iterable
# try:
#     from collections.abc import Iterable
# except ImportError:
#     from collections import Iterable

nltk.download('words')
nltk.download('punkt')

# data = set(map(lambda x: x.lower(), list(words.words())))
data = []
with open('eng_words_uk_us.csv', newline='') as inputfile:
    for row in csv.reader(inputfile):
        data.append(row[0].lower())


nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

def propn_identification_pos(text):
    doc = nlp(text)
    for tok in doc:
        st.sidebar.write(tok, tok.pos_)
    # Proper Noun, ORG identification from given query/string/text_file
    propn_ents = set()

    for token in doc:
        if token.lemma_ not in data and not token.is_punct and token.is_ascii and token.is_alpha and not token.is_stop:
            if token.pos_ in ("PROPN", "NOUN", "ADJ", "INTJ") and len(token.text) > 2:
                propn_ents.add(token)

    propn_set = set()
    for tok in propn_ents:
        if tok.text.lower() not in data:
            propn_set.add(tok.text)

    propn_list = [x.lower() for x in list(propn_set)]
    return propn_list

def propn_identification_without_pos(text):
    doc = nlp(text.lower())
    text = " ".join([token.lemma_ for token in doc])
    tokens = word_tokenize(text)

    propn_list = []
    for i in tokens:
        # print(i.lower() not in data)
        # print(i.isalpha())
        if i.lower() not in data and i.isalpha():
            propn_list.append(removeConsecutiveDuplicates(i, k=3))
    return propn_list


def propn_engmis_enchant(text):
    d = enchant.Dict("en_US")
    propn_list = []
    word_list = []
    doc = nlp(text.lower())
    text = " ".join([token.lemma_ for token in doc])
    tokens = word_tokenize(text)

    tokens = list(set(tokens))
    for i in tokens:
        if i.isalpha():
            word_list.append(i)
    for i in word_list:
        if d.check(i) != True and len(i) > 2:
            propn_list.append(removeConsecutiveDuplicates(i, k=3))

    return propn_list
