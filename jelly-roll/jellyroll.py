# -*- coding: utf-8 -*-
"""
Created on Tue May 10 18:58:26 2022

@author: Alex Boisvert

Helper lookup for making "jelly roll" puzzles
"""

import itertools
import os
from collections import defaultdict
import json
import zipfile

# The smallest length for words in the puzzle
MIN_WORD_LENGTH = 4
# The minimum overlap of words
MIN_OVERLAP = 1
# Minimum score of word list entries
MIN_SCORE = 50
# The word list to use
WORDLIST_DIR = os.path.join('..', 'word_lists')
word_list = 'spreadthewordlist.dict'
WORDLIST = os.path.join(WORDLIST_DIR, word_list)

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
    cuts = list(range(0, n+1))
    if num:
        num_arr = [num-1]
    else:
        num_arr = range(n)
    for k in num_arr:
        for cutpoints in itertools.combinations_with_replacement(cuts, k):
            yield multiSlice(s, cutpoints)
            
# take pairs of letters from a word
def pairs_of_letters(word_orig):
    # The "keys" of ret are the offset of the word
    # we're interested in 0, 1, 2
    ret = ['', '', '']
    for offset in range(len(ret)):
        remainder = ''
        word = word_orig
        addition, word = word[:2 - offset], word[2 - offset:]
        remainder += addition
        while word:
            addition, word = word[2:4], word[4:]
            remainder += addition
        ret[offset] = remainder
    return ret
            
#%% Read in word list
ALL_WORDS = set()
beginnings = set()
ends = set()

# dictionary of word -> pairs_of_letters
offset_starts = dict()
# dictionary of "finishers" to word beginnings
begin_end_dict = defaultdict(set)

with open(WORDLIST, 'r') as fid:
    for line in fid:
        word, score = line.upper().split(';')
        score = int(score)
        if score >= MIN_SCORE and len(word) >= MIN_WORD_LENGTH:
            ALL_WORDS.add(word)
            # Partition the word to take the beginning and end parts
            for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
                w1, w2 = word[:n], word[n:]
                beginnings.add(w1)
                ends.add(w2)
                
                # we need to find words that finish certain "beginnings"
                # they don't have to "finish" it, just continue it
                for n2 in range(MIN_WORD_LENGTH//2, MIN_WORD_LENGTH+2):
                    w3 = w2[:n2]
                    begin_end_dict[w1].add(w3)
                
            offset_starts[word] = pairs_of_letters(word)

begin_keys = frozenset(begin_end_dict.keys())
            
#%% Make word partitions
# for each word we need to take all partitions of the odd and even
# and we need to see which "beginnings" they can end
# and of course we need to ensure that their "endings" are valid "beginnings"
prev_word_count = 1e6
new_word_count = 0
good_words = ALL_WORDS.copy()

changed_values = (True, True, True)

while max(changed_values):
    gw = set()
    begin_dict = dict()
    end_dict = dict()
    begin_pair_arr = [defaultdict(set), defaultdict(set), defaultdict(set)]
    for word in good_words:
        # see if a partition of the one_two results in endings and beginnings
        os = offset_starts[word]
        # we can keep this word if there's a partition of both that's good
        good_ct = [False, False, False]
        this_begin_dict = defaultdict(set)
        this_end_dict = defaultdict(set)
        for i, w in enumerate(os):
            for n in range(MIN_OVERLAP, len(w) - MIN_OVERLAP + 1):
                w1, w2 = w[:n], w[n:]
                if w2 in beginnings and w1 in ends:
                    this_word = word
                    this_begin_dict[w1] |= set([this_word])
                    this_end_dict[w2] |= set([this_word])
                    begin_pair_arr[i][w1] |= set([this_word])
                    good_ct[i] = True
        if min(good_ct):
            for k, v in this_begin_dict.items():
                begin_dict[k] = begin_dict.get(k, set()).union(v)
            for k, v in this_end_dict.items():
                end_dict[k] = end_dict.get(k, set()).union(v)
            gw.add(word)
            
    print(len(good_words))
    orig_lengths = (len(good_words), len(beginnings), len(ends))
    good_words = good_words.intersection(gw)
    print(len(good_words))
    beginnings = beginnings.intersection(set(begin_dict.keys()))
    ends = ends.intersection(set(end_dict.keys()))
    new_lengths = (len(good_words), len(beginnings), len(ends))
    changed_values = [orig_lengths[i] == new_lengths[i] for i in range(len(orig_lengths))]
    
# Remove blank entries from begin_pair_arr
tmp = [{}, {}, {}]
begin_pair_arr2 = [{}, {}, {}]
for i, d in enumerate(begin_pair_arr):
    for k, v in d.items():
        if v:
            tmp[i][k] = v
            begin_pair_arr2[i][k] = list(v)
begin_pair_arr = tmp

#%% Write file to zipped JSON for JS purposes
# Note that we can create "begin_keys" from begin_end_dict in JS

begin_end_dict2 = dict((k, list(v)) for k, v in begin_end_dict.items())

j = {
  "good_words": list(good_words)
, "begin_end_dict": begin_end_dict2
, "begin_pair_arr": begin_pair_arr2
}

# Convert the Python object to a JSON string
json_data = json.dumps(j)

# Create a new ZIP file and add the JSON data to it
with zipfile.ZipFile("jellyroll.json.zip", 'w', zipfile.ZIP_DEFLATED) as zip_file:
    # Write JSON data to a file inside the ZIP
    zip_file.writestr("jellyroll.json", json_data)

#%%
def add_word(word, all_words, white_words, gray_words):
    """
    Add a word to all_words. This updates one and two words too.
    """
    all_words2 = all_words + [word]
    all_string = ''.join(all_words2)
    white_string = ''.join(white_words)
    gray_string = ''.join(gray_words)
    
    # We have to pull out any "one" or "two" words 
    # that resulted from adding our word
    white_start = pairs_of_letters(all_string)[1][len(white_string):]
    gray_start = pairs_of_letters(all_string[1:])[0][len(gray_string):]
    
    white_words2, gray_words2 = white_words, gray_words
    
    if begin_end_dict.get(white_start):
        # it's okay if there are future words we can make from this
        pass
    else:
        for i in range(1, len(white_start)):
            if white_start[:-i] in good_words:
                white_words2 = white_words2 + [white_start[:-i]]
                white_start = white_start[-i:]
                break
    if begin_end_dict.get(gray_start):
        pass
    else:
        for i in range(1, len(gray_start)):
            if gray_start[:-i] in good_words:
                gray_words2 = gray_words2 + [gray_start[:-i]]
                gray_start = gray_start[-i:]
                break
    return all_words2, white_words2, gray_words2, white_start, gray_start
    
def does_word_work(word, all_words, white_words, gray_words):
    """
    Check if a word works with our current words
    """
    # Add the word to our list
    all_words2, white_words2, gray_words2, white_start, gray_start = add_word(word, all_words, white_words, gray_words)
    all_string = ''.join(all_words2)

    # We start with white if the length mod 4 is 0 or 3
    start_white = False
    if len(all_string) % 4 in (0, 3):
        start_white = True
        
    # We start with one letter if the length is even
    start_one = False
    if len(all_string) % 2 == 0:
        start_one = True
    
    # find a new "all" word that "ends" both the words
    white_endings = begin_end_dict[white_start]
    gray_endings = begin_end_dict[gray_start]
    next_white = set()
    next_gray = set()

    if not start_white and not start_one:
        for x in gray_endings:
            next_gray |= begin_pair_arr[0].get(x, set())
        for x in white_endings:
            next_white |= begin_pair_arr[2].get(x, set())
    elif start_white and not start_one:
        for x in gray_endings:
            next_gray |= begin_pair_arr[2].get(x, set())
        for x in white_endings:
            next_white |= begin_pair_arr[0].get(x, set())
    elif start_white and start_one:
        for x in gray_endings:
            next_gray |= begin_pair_arr[2].get(x, set())
        for x in white_endings:
            next_white |= begin_pair_arr[1].get(x, set())
    elif not start_white and start_one:
        for x in gray_endings:
            next_gray |= begin_pair_arr[1].get(x, set())
        for x in white_endings:
            next_white |= begin_pair_arr[2].get(x, set())
            
    possible_next_words = next_gray & next_white
    
    # Instead of doing a recursive check, just ensure
    # that the "ends" of these are valid "beginnings"
    ret = set()
    for pnw in possible_next_words:
        _, _, _, white_start, gray_start = add_word(pnw, all_words2, white_words2, gray_words2)
        if white_start in begin_keys and gray_start in begin_keys:
            ret.add(pnw)
    return ret

def next_inner_words(word, all_words, white_words, gray_words):
    """
    Print the next "inner" words that would arise if we added "word"
    """
    _, white_words2, gray_words2, white_start, gray_start = add_word(word, all_words, white_words, gray_words)
    return [' '.join(white_words2[len(white_words):]), ' '.join(gray_words2[len(gray_words):]), white_start, gray_start]
    
def next_word_sorter(next_word, all_words, white_words, gray_words):
    """
    Sort "next words" by length descending
    """
    next_white, next_gray, white_start, gray_start = next_inner_words(next_word, all_words, white_words, gray_words)
    white_len, gray_len = len(''.join(next_white)), len(''.join(next_gray))
    if not white_len:
        white_len = len(white_start) + 2
    if not gray_len:
        gray_len = len(gray_start) + 2
    return white_len + gray_len + len(next_word)
    
#%%
all_words, white_words, gray_words = [], [], []
word = 'runinto'

word = word.upper()

while True:
    # Print our possibles
    next_words = does_word_work(word, all_words, white_words, gray_words)
    if next_words:
        all_words, white_words, gray_words, white_start, gray_start = add_word(word, all_words, white_words, gray_words)
        # Print our current length
        print(len(''.join(all_words)))
        print(all_words, white_words, gray_words)
        print(white_start, gray_start)
        next_words = sorted(next_words, key=lambda x: next_word_sorter(x, all_words, white_words, gray_words), reverse=True)
        for nw in next_words[:15]:
            niw = next_inner_words(nw, all_words, white_words, gray_words)
            print(' / '.join([nw] + niw))
    else:
        # What do we do in this case?
        print("No further fill found. Backtracking needed.")
        break
    
    # Do a loop for choosing the next word
    word = input("Enter the next word: ").upper()
    remain_in_loop = True
    while remain_in_loop:
        if does_word_work(word, all_words, white_words, gray_words):
            remain_in_loop = False
        else:
            word = input("That word doesn't work. Choose another: ").upper()
            
        
    
