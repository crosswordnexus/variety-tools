#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the word lists for CC puzzles

Created on Fri Jan 14 14:21:10 2022

@author: Alex Boisvert
"""
import itertools
import json
from pathlib import Path
import re

# The smallest length for words
MIN_WORD_LENGTH = 5
# Smallest length for consonant-words
MIN_CONSONANT_LENGTH = 3
# The minimum overlap of words
MIN_OVERLAP = 1
# Minimum score of word list entries
MIN_SCORE = 50

#%% Helper functions

# Make partitions of a string
def multiSlice(s, cutpoints):
    """
    Helper function for allPartitions
    """
    k = len(cutpoints)
    if k == 0:
        return [s]
    else:
        multislices = [s[:cutpoints[0]]]
        multislices.extend(s[cutpoints[i]:cutpoints[i+1]] for i in range(k-1))
        multislices.append(s[cutpoints[k-1]:])
        return multislices

# This includes partitions of length 0
def allPartitions(s, num=None):
    n = len(s)
    cuts = list(range(0,n+1))
    if num:
        num_arr = [num-1]
    else:
        num_arr = range(n)
    for k in num_arr:
        for cutpoints in itertools.combinations_with_replacement(cuts,k):
            yield multiSlice(s,cutpoints)
            
def consonants_only(s):
    """
    Return only the consonants from a string
    """
    return re.sub(r'[^BCDFGHJKLMNPQRSTVWXZ]+', '', s)

#%% Read in word list
all_words = set()
beginnings = set()
ends = set()
all_word_dict = dict()

base = Path(__file__).parent        # directory containing this file
target = base / '..' / 'word_lists' / 'spreadthewordlist.dict'
WORDLIST = target.resolve()

# Dictionary for looking up a word from its consonants only
# We keep ... all of them, I guess
consonants_to_words = dict()

# Loop through the word list
with open(WORDLIST, 'r') as fid:
    for line in fid:
        word1, score = line.split(';')
        word1 = word1.upper()
        score = int(score)
        
        # Skip if the word contains the letter "Y"
        if "Y" in word1:
            continue
        
        # The "word" is the consonants only
        word = consonants_only(word1)
        
        # Skip if the word is all consonants
        if word == word1:
            continue

        if score >= MIN_SCORE \
            and len(word1) >= MIN_WORD_LENGTH \
            and len(word) >= MIN_CONSONANT_LENGTH:
            
            # Add to our lookup table
            consonants_to_words[word] = consonants_to_words.get(word, []) + [word1]
            
            all_words.add(word)
            all_word_dict[word] = len(word)
            # Partition the word to take the beginning and end parts
            for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
                w1, w2 = word[:n], word[n:]
                beginnings.add(w1)
                ends.add(w2)

#%% Create needed dictionaries
prev_word_count = 1e6
new_word_count = 0
good_words = all_words.copy()
# Now go through the words again to see if it's admissible

while new_word_count < prev_word_count:
    gw = set()
    starter_words = dict()
    begin_dict = dict()
    end_dict = dict()
    for word in good_words:
        for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
            w1, w2 = word[:n], word[n:]
            # Starter words
            if w1 in all_words and len(w1) >= 4 and w2 in beginnings:
                starter_words[word] = starter_words.get(word, set()).union([w2])
            
            if w2 in beginnings and w1 in ends:
                this_word = (word, None)
                begin_dict[w1] = begin_dict.get(w1, set()).union([this_word])
                end_dict[w2] = end_dict.get(w2, set()).union([this_word])
                gw.add(word)
    #prev_word_count = len(good_words)
    #new_word_count = len(gw)
    good_words = gw.copy()

    prev_word_count = len(beginnings)
    beginnings = set(begin_dict.keys())
    ends = set(end_dict.keys())
    new_word_count = len(beginnings)
    
    print(f"Previous beginnings: {prev_word_count} - new beginnings: {new_word_count}")


print(f"Good words: {len(good_words)}")

# Now add any words that have a hidden word in them
# but that still work with a beginning / end
for word in all_words:
    for p in allPartitions(word, 3):
        w1, w_m, w2 = p
        if w1 in beginnings and w2 in ends and w_m in all_words:
            this_word = (word, w_m)
            begin_dict[w1] = begin_dict.get(w1, set()).union([this_word])
            end_dict[w2] = end_dict.get(w2, set()).union([this_word])
            good_words.add(word)

print(f"Good words (after adding hidden words): {len(good_words)}")

#%% Make one global dictionary from this and serialize into JSON format

helper_dict = dict()
items = {'begin': begin_dict}
for name, d in items.items():
    helper_dict[name] = dict()
    for _str, this_set in d.items():
        helper_dict[name][_str] = []
        for this_word in this_set:
            w0, w1 = this_word
            score = all_word_dict.get(w0, len(w0))
            if w1:
                score = (score + all_word_dict.get(w1, len(w1))) / 2
            leftover_len = len(w0) - len(_str)
            if w1 is not None:
                leftover_len -= len(w1)
            if name == 'begin':
                leftover = w0[-leftover_len:]
            else:
                leftover = w0[:leftover_len]
            d2 = {'words': [w0, w1], 'score': score, 'leftover': leftover}
            helper_dict[name][_str].append(d2)

# Write out this file for JavaScript purposes
with open('helper_dict.json', 'w') as fid:
    json.dump(helper_dict, fid)      

# Write a file of consonants_to_words
with open('consonants_to_words.json', 'w') as fid:
    json.dump(consonants_to_words, fid)      

#%% Find words to finish up a CC puzzle
ret = []
# Letters that will start side 1
letters1 = 'S'
# Number of letters remaining on both sides
num1, num2 = 11, 13

for w1, w0 in begin_dict[letters1]:
    for word1 in consonants_to_words[w1]:
        if len(word1) != num1:
            continue
        
        if w0 is None:
            # Take what remains of w1 for side 2
            w2 = w1[len(letters1):]
            for word2 in consonants_to_words.get(w2, []):
                if len(word2) == num2:
                    print(word1, word2)
        else:
            w2 = w1[len(letters1) + len(w0):]
            for word0 in consonants_to_words.get(w0, []):
                for word2 in consonants_to_words.get(w2, []):
                    if len(word0) + len(word2) == num2:
                        ret.append((word1, word0, word2))

