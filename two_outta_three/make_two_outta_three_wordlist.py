# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 08:58:06 2022

@author: Alex Boisvert

Create tools to help with creating "Two Outta Three Ain't Bad" puzzles
"""
import nprcommontools as nct
import rhyme
import json
import math
import os

words = dict()
MIN_SCORE = 80
# Word list with only Scrabble-eligible words
wordlist_file = os.path.join('..', 'word_lists', 'kaidoku_wordlist.dict')
with open(wordlist_file, 'r') as fid:
    for line in fid:
        line = line.strip().lower()
        word, score = line.split(';')
        score = int(score)
        if score >= MIN_SCORE:
            words[word] = math.floor(score)

word_set = frozenset(words.keys())

#%% Create a dictionary for rhymes
rhyme_dict = dict()
word_to_rhyme_keys = dict()
for w in word_set:
    prons = rhyme._cdict.get(w, [])
    for p in prons:
        try:
            num_syllables = rhyme.syllables(p, is_pron=True)
            rhyming_part = tuple(rhyme.rhyming_part(p))
            rhyme_dict[(rhyming_part, num_syllables)] = rhyme_dict.get((rhyming_part, num_syllables), []) + [w]
            word_to_rhyme_keys[w] = word_to_rhyme_keys.get(w, []) + [(rhyming_part, num_syllables)]
        except:
            pass
        
#%% Helper function to find all rhymes
def find_rhymes(word):
    word = word.lower()
    rhymes = set()
    rkeys = word_to_rhyme_keys.get(word, [])
    for rk in rkeys:
        for w in rhyme_dict.get(rk, []):
            if w != word:
                rhymes.add(w)
    return rhymes
    
# Helper function for "good" word pairs
# They need to not have half or more of the letters in the same spot
# or start with the same four letters
def num_same_letters(w1, w2):
    assert len(w1) == len(w2)
    ret = 0
    for i, c in enumerate(w1):
        if c == w2[i]:
            ret += 1
    return ret

def is_good_pair(w1, w2):
    if len(w1) == len(w2):
        if num_same_letters(w1, w2) >= len(w1)/2:
            return False
    if min(len(w1), len(w2)) >= 4:
        if w1[:4] == w2[:4]:
            return False
    if min(len(w1), len(w2)) >= 5:
        if w1[-5:] == w2[-5:]:
            return False
    return True

#%% Look for synonym / anagram / rhyme
good_words = dict()
sorted_dict = nct.make_sorted_dict(word_set)
for word in word_set:
    # count number of anagrams
    anagrams = sorted_dict.get(nct.sort_string(word), []).copy()
    for a in anagrams.copy():
        if not is_good_pair(a, word):
            anagrams.remove(a)
    num_anagrams = len(anagrams)
    # count number of synonyms
    synonyms = nct.get_synonyms(word).intersection(word_set)
    for s in synonyms.copy():
        if not is_good_pair(s, word):
            synonyms.remove(s)
    num_synonyms = len(synonyms)
    # we need one of those to continue
    if anagrams or synonyms:
        # get rhymes
        rhymes = find_rhymes(word)
        for r in rhymes.copy():
            if not is_good_pair(r, word):
                rhymes.remove(r)
        num_rhymes = len(rhymes)
        if int(num_anagrams > 0) + int(num_synonyms > 0) + int(num_rhymes > 0) >= 2:
            score = 70
            # We prioritize rhyme / anagram pairs
            if num_anagrams > 0:
                score += 4
            if num_rhymes > 0:
                score += 2
            if num_synonyms > 0:
                score += 1
            good_words[word] = {'score': score, 'rhymes': list(rhymes), 'anagrams': anagrams, 'synonyms': list(synonyms)}
    
#%% Write to a file
with open('two_outta_three.dict', 'w') as fid:
    for w, v in good_words.items():
        fid.write(f"""{w.upper()};{v['score']}\n""")
        
with open('two_outta_three.json', 'w') as fid:
    json.dump(good_words, fid)
    
#%% Read in good_words
with open('two_outta_three.json', 'r') as fid:
    good_words = json.load(fid)
    
#%% What options do we have for a given word?

word = 'wrote'

word_lower = word.lower()
print(good_words[word_lower])

