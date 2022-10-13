import sys
from functions import *
from propn_identification import *
import streamlit as st
import nltk
from nltk.corpus import words
from abydos.phonetic import nysiis
from abydos.distance import dist_cosine
from abydos.distance import Levenshtein
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



if submit:
    propn_list = propn_identification_without_pos(text)
    st.sidebar.write(propn_list)
    eng_mis_corrected = {}

    client = connect_elasticsearch()
    for name in propn_list:
        nysiis_code_name = nysiis(name)

        target_index = "spell_checker_index"

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
            results = matcher(client, target_index, nysiis_code_name)

            for i in results:
                sim_words.append(i['_source']['name'])

            for i in results:
                sim_engwords.append(i['_source']['word'])


        print(sim_words)
        print(sim_engwords)
 

        similar_word_preference = {}
        cmp = Levenshtein()

        for word in sim_words:
            if name in propn_list:
                name = removeConsecutiveDuplicates(name, k=3)
                if len(name) < 5 and dist_cosine(nysiis(word), nysiis(name)) == 0 and int(cmp.alignment(word, name)[0]) < 2 and name != word:
                # if len(name) < 8 and dist_cosine(word, name) < 0.3 and Levenshtein(word, name) < 3 and name != word:
                    similar_word_preference[word] = dist_cosine(word, name)
                if 5 <= len(name) < 7 and dist_cosine(nysiis(word), nysiis(name)) < 0.3 and int(cmp.alignment(word, name)[0]) < 3 and name != word:
                # if len(name) < 8 and dist_cosine(word, name) < 0.3 and levenshteinDistanceDP(word, name) < 3 and name != word:
                    similar_word_preference[word] = dist_cosine(word, name)
                elif 7 <= len(name) <= 9 and dist_cosine(nysiis(word), nysiis(name)) < 0.3 and int(cmp.alignment(word, name)[0]) < 3 and name != word:
                # elif 8 <= len(name) <= 9 and dist_cosine(nysiis(word), nysiis(name)) < 0.5 and levenshteinDistanceDP(word, name) < 3 and name != word:
                    similar_word_preference[word] = dist_cosine(word, name)
                elif len(name) > 9 and dist_cosine(nysiis(word), nysiis(name)) < 0.3 and int(cmp.alignment(word, name)[0]) < 5 and name != word:
                # elif len(name) > 9 and dist_cosine(word, name) < 0.3 and levenshteinDistanceDP(word, name) < 3 and name != word:
                    similar_word_preference[word] = dist_cosine(word, name)
            # else:
            #     if len(name) < 8 and dist_cosine(nysiis(word), nysiis(name)) < 0.3 and levenshteinDistanceDP(word,  name) < 3:
            #         similar_word_preference[word] = dist_cosine(nysiis(word), nysiis(name))
            #     elif 8 <= len(name) <= 9 and dist_cosine(nysiis(word), nysiis(name)) < 0.3 and levenshteinDistanceDP(word, name) < 3:
            #         similar_word_preference[word] = dist_cosine(nysiis(word), nysiis(name))
            #     elif len(name) > 9 and dist_cosine(nysiis(word), nysiis(name)) < 0.3 and levenshteinDistanceDP(word, name) < 5:
            #         similar_word_preference[word] = dist_cosine(nysiis(word), nysiis(name))

            # print(name, word, levenshteinDistanceDP(name, word), dist_cosine(name, word), dist_cosine(nysiis(name), nysiis(word)))

        sort_sim_word = sorted(similar_word_preference.items(), key=lambda item: item[1])
        # print(sort_sim_word)
        # print(similar_word_preference)

        # print(similar_word_preference)


        sim_word_score = []
        for i in sort_sim_word:
            sim_word_score.append(i[0])

        sample_dict = {}
        key = name
        list_of_values = sim_word_score[0:4]


        a = add_values_in_dict(sample_dict, key, list_of_values)
        if len(a) != 0:
            st.write(a)
            # st.write(a | eng_mis_corrected)
            # st.write(eng_mis_corrected)
        # st.write(add_values_in_dict(sample_dict, key, list_of_values))

