#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spiral-generating code

Created on Fri Jan 14 14:21:10 2022

@author: Alex Boisvert
"""
import gzip
import itertools
import json
import wordninja
import re
from pathlib import Path

# The smallest length for words in the puzzle
MIN_WORD_LENGTH = 5
# The minimum overlap of words
MIN_OVERLAP = 2
# Minimum score of word list entries
MIN_SCORE = 50
# The word list(s) to use
WORDLISTS = ['spreadthewordlist.dict', 'nediger_99.txt']
WORDLIST_DIR = Path('../word_lists')

# %% Helper functions

def alpha_only(s):
    return re.sub(r'[^A-Z]+', '', s.upper())

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
    cuts = list(range(0, n+1))
    if num:
        num_arr = [num-1]
    else:
        num_arr = range(n)
    for k in num_arr:
        for cutpoints in itertools.combinations_with_replacement(cuts, k):
            yield multiSlice(s, cutpoints)


# %% Read in word list(s)
all_words = set()
beginnings = set()
ends = set()
all_word_dict = dict()

for wl in WORDLISTS:
    wordlist = WORDLIST_DIR / wl
    with open(wordlist, 'r') as fid:
        for line in fid:
            word, score = line.upper().split(';')
            word = alpha_only(word)
            score = int(score)
            if score >= MIN_SCORE and len(word) >= MIN_WORD_LENGTH:
                all_words.add(word)
                all_word_dict[word] = score
                # Partition the word to take the beginning and end parts
                for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
                    w1, w2 = word[:n], word[n:]
                    beginnings.add(w1)
                    ends.add(w2)

# %% Create needed dictionaries
prev_word_count = 1e6
new_word_count = 0
good_words = all_words.copy()
# Now go through the words again to see if it's admissible

while new_word_count < prev_word_count:
    gw = set()
    begin_dict = dict()
    end_dict = dict()
    for word in good_words:
        # Split with wordninja so we don't get degenerate cases
        subwords = set(wordninja.split(word))
        for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
            w1, w2 = word[:n], word[n:]
            if (
                w2 in beginnings 
                and w1 in ends 
                and w1 not in subwords
                and w2 not in subwords
            ):
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


print(len(good_words))

# Now add any words that have a hidden word in them
# but that still work with a beginning / end
for word in all_words:
    # split with wordninja to avoid degenerate cases
    subwords = subwords = set(wordninja.split(word))
    for p in allPartitions(word, 3):
        w1, w_m, w2 = p
        if (
            w2 in beginnings 
            and w1 in ends 
            and w_m in all_words
            and not set([w1, w_m, w2]) & subwords
        ):
            this_word = (word, w_m)
            begin_dict[w1] = begin_dict.get(w1, set()).union([this_word])
            end_dict[w2] = end_dict.get(w2, set()).union([this_word])
            good_words.add(word)
            #if len(w_m) == 5:
            #    print(word, w_m)

print(len(good_words))

# %% Make one global dictionary from this and serialize into JSON format

# The default word score (mostly for missing words)
DEF_WORD_SCORE = 0.85 * MIN_SCORE

helper_dict = dict()
items = {'begin': begin_dict}
for name, d in items.items():
    helper_dict[name] = dict()
    for _str, this_set in d.items():
        helper_dict[name][_str] = []
        for this_word in this_set:
            w0, w1 = this_word
            #score = all_word_dict.get(
            #    w0, DEF_WORD_SCORE) + all_word_dict.get(w1, DEF_WORD_SCORE)
            score = len(w0)
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
with gzip.open('helper_dict.json.gz', 'wt', encoding='utf-8') as fid:
    json.dump(helper_dict, fid)

