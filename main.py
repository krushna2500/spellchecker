import sys
from functions import *
from propn_identification import *
import streamlit as st
import nltk
from nltk.corpus import words
from abydos.phonetic import nysiis
from abydos.distance import dist_cosine
from abydos.distance import Levenshtein
from abydos.phonetic import RefinedSoundex
from elastic_injection_query import *

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable



form = st.form(key='my-form')
text = form.text_input('Enter your text')
sentences = nltk.sent_tokenize(text)  # whole paragraph break into sentence.
data = set(map(lambda x: x.lower(), list(words.words())))
submit = form.form_submit_button('Submit')

propn_list = propn_identification_without_pos(text)
print("*****************************************************", propn_list)


if submit:
    st.sidebar.write(propn_list)
    eng_mis_corrected = {}

    client = connect_elasticsearch()
    for name in propn_list:
        nysiis_code_name = nysiis(name)
        soundex = RefinedSoundex()
        soundex_embb_name = soundex.encode(name)

        target_index = "spell_checker_alias"
        check = matcher_name_check(client, target_index, name)
        name_check = []
        for i in check:
            name_check.append(i['_source']['name'])

        engword_check = []
        for i in check:
            engword_check.append(i['_source']['word'])


        sim_words = []
        sim_engwords = []
        eng_misspelled_words = []
        if len(name) != 0 and len(name_check) == 0:  # We can use try expect also
            # results = matcher(client, target_index, nysiis_code_name)
            results = matcher_fuzzy_elastic(client, target_index, name)

            for i in results:
                sim_words.append(i['_source']['name'].lower())

            for i in results:
                sim_engwords.append(i['_source']['worde'].lower())
        sim_words = list(set(sim_words))
        sim_engwords = list(set(sim_engwords))
        print("####################################################", propn_list, nysiis_code_name)
        print("****************************************************", sim_words)

        st.write(nysiis_code_name)

        similar_word_preference = {}
        cmp = Levenshtein()

        # for word in sim_words:
        #     if name in propn_list:
        #         name = removeConsecutiveDuplicates(name, k=3)
        #         if len(name) < 5 and dist_cosine(nysiis(word), nysiis_code_name) == 0 and int(cmp.alignment(word, name)[0]) < 2 and name != word:
        #             similar_word_preference[word] = dist_cosine(word, name)
        #         if 5 <= len(name) < 7 and dist_cosine(nysiis(word), nysiis_code_name) < 0.3 and int(cmp.alignment(word, name)[0]) < 3 and name != word:
        #             similar_word_preference[word] = dist_cosine(word, name)
        #         elif 7 <= len(name) <= 9 and dist_cosine(nysiis(word), nysiis_code_name) < 0.3 and int(cmp.alignment(word, name)[0]) < 3 and name != word:
        #             similar_word_preference[word] = dist_cosine(word, name)
        #         elif len(name) > 9 and dist_cosine(nysiis(word), nysiis_code_name) < 0.3 and int(cmp.alignment(word, name)[0]) < 5 and name != word:
        #             similar_word_preference[word] = dist_cosine(word, name)


        for word in sim_words:
            if name in propn_list:
                name = removeConsecutiveDuplicates(name, k=3)
                if len(name) < 5 and soundex.encode(word) == soundex_embb_name and name != word and dist_cosine(name, word):
                    similar_word_preference[word] = dist_cosine(word, name)
                elif 5 <= len(name) < 7 and soundex.encode(word) == soundex_embb_name and name != word and dist_cosine(name, word):
                    similar_word_preference[word] = dist_cosine(word, name)
                elif 7 <= len(name) <= 9 and soundex.encode(word) == soundex_embb_name and name != word and dist_cosine(name, word):
                    similar_word_preference[word] = dist_cosine(word, name)
                elif len(name) > 9 and soundex.encode(word) == soundex_embb_name and name != word and dist_cosine(name, word) < 0.5:
                    similar_word_preference[word] = dist_cosine(word, name)


        sort_sim_word = (sorted(similar_word_preference.items(), key=lambda item: item[1]))
        print(sort_sim_word)
        sim_word_score = []
        for i in sort_sim_word:
            sim_word_score.append(i[0])

        sample_dict = {}
        key = name
        list_of_values = sim_word_score[0:10]


        a = add_values_in_dict(sample_dict, key, list_of_values)
        if len(a) != 0:
            st.write(a)

