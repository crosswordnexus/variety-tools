# -*- coding: utf-8 -*-
"""
Created on Tue May 10 18:58:26 2022

@author: Alex Boisvert

Helper lookup for making "two-tone" puzzles
"""

import itertools
import os
from collections import defaultdict
import trie

# The smallest length for words in the puzzle
MIN_WORD_LENGTH = 4
# The minimum overlap of words
MIN_OVERLAP = 1
# Minimum score of word list entries
MIN_SCORE = 50
# The word list to use
WORDLIST_DIR = r'C:\Users\boisv\Documents\word_lists'
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
            
#%% Read in word list
all_words = set()
beginnings = set()
ends = set()
all_word_dict = dict()

# dictionary of word -> odd, even letters
odd_even = dict()
# dictionary of "finishers" to word beginnings
begin_end_dict = defaultdict(set)

with open(WORDLIST, 'r') as fid:
    for line in fid:
        word, score = line.upper().split(';')
        score = int(score)
        if score >= MIN_SCORE and len(word) >= MIN_WORD_LENGTH:
            all_words.add(word)
            all_word_dict[word] = score
            # retain the odd and even letters
            odd = word[::2]
            even = word[1::2]
            # Partition the word to take the beginning and end parts
            for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
                w1, w2 = word[:n], word[n:]
                beginnings.add(w1)
                ends.add(w2)
                
                # we need to find words that finish certain "beginnings"
                begin_end_dict[w1].add(w2)
            
            odd_even[word] = {'odd': odd, 'even': even}
            
#%% Make word partitions
# for each word we need to take all partitions of the odd and even
# and we need to see which "beginnings" they can end
# and of course we need to ensure that their "endings" are valid "beginnings"
prev_word_count = 1e6
new_word_count = 0
good_words = all_words.copy()

changed_values = (True, True, True)

while max(changed_values):
    gw = set()
    begin_dict = dict()
    end_dict = dict()
    begin_even_dict = dict()
    begin_odd_dict = dict()
    for word in good_words:
        # see if a partition of the odd/even results in endings and beginnings
        even, odd = odd_even[word]['even'], odd_even[word]['odd']
        # we can keep this word if there's a partition of both that's good
        good_ct = [False, False]
        this_begin_dict = dict()
        this_end_dict = dict()
        for i, w in enumerate((odd, even)):
            for n in range(MIN_OVERLAP, len(w) - MIN_OVERLAP + 1):
                w1, w2 = w[:n], w[n:]
                if w2 in beginnings and w1 in ends:
                    this_word = word
                    this_begin_dict[w1] = this_begin_dict.get(w1, set()).union([this_word])
                    this_end_dict[w2] = this_end_dict.get(w2, set()).union([this_word])
                    if i == 0:
                        begin_odd_dict[w1] = begin_odd_dict.get(w1, set()).union([this_word])
                    if i == 1:
                        begin_even_dict[w1] = begin_even_dict.get(w1, set()).union([this_word])
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

# Make the Trie from the good words
prefixTrie = trie.Trie()
for word in good_words:
    prefixTrie.insert(word)

#%%
def add_word(word, all_words, even_words, odd_words):
    """
    Add a word to all_words. This updates even and odd words too.
    """
    all_words2 = all_words + [word]
    all_string = ''.join(all_words2)
    even_string = ''.join(even_words)
    odd_string = ''.join(odd_words)
    
    # We have to pull out any odd or even words that resulted from adding our word
    odd_start = all_string[::2][len(odd_string):]
    even_start = all_string[1::2][len(even_string):]
    
    even_words2, odd_words2 = even_words, odd_words
    
    if prefixTrie.search(even_start):
        # it's okay if there are future words we can make from this
        pass
    else:
        for i in range(1, len(even_start)):
            if even_start[:-i] in good_words:
                even_words2 = even_words2 + [even_start[:-i]]
                even_start = even_start[-i:]
                break
    if prefixTrie.search(odd_start):
        pass
    else:
        for i in range(1, len(odd_start)):
            if odd_start[:-i] in good_words:
                odd_words2 = odd_words2 + [odd_start[:-i]]
                odd_start = odd_start[-i:]
                break
    return all_words2, even_words2, odd_words2, even_start, odd_start
    

def does_word_work(word, all_words, even_words, odd_words, num_lookaheads=1):
    """
    Check if a word works with our current words
    """
    # Add the word to our list
    all_words2, even_words2, odd_words2, even_start, odd_start = add_word(word, all_words, even_words, odd_words)
    all_string = ''.join(all_words2)

    # `start_even` is True if the next letter in "all" words continues `even_start`
    start_even = len(all_string) % 2 == 1
    
    # find a new "all" word that ends both the words
    even_endings = begin_end_dict[even_start]
    odd_endings = begin_end_dict[odd_start]
    next_even = set()
    next_odd = set()

    if not start_even:
        for x in even_endings:
            next_even = next_even.union(begin_even_dict.get(x, set()))
        for x in odd_endings:
            next_odd = next_odd.union(begin_odd_dict.get(x, set()))
    else:
        for x in even_endings:
            next_even = next_even.union(begin_odd_dict.get(x, set()))
        for x in odd_endings:
            next_odd = next_odd.union(begin_even_dict.get(x, set()))
            
    possible_next_words = next_even.intersection(next_odd)
    
    if num_lookaheads == 0:
        return possible_next_words
    
    ret = set()
    for nw in possible_next_words:
        if does_word_work(nw, all_words2, even_words2, odd_words2, num_lookaheads-1):
            ret.add(nw)
            
    return ret
    
#%%
all_words, even_words, odd_words = [], [], []
word = 'SPEEDO'

while True:
    # Print our possibles
    next_words = does_word_work(word, all_words, even_words, odd_words, num_lookaheads=1)
    if next_words:
        all_words, even_words, odd_words, even_start, odd_start = add_word(word, all_words, even_words, odd_words)
        # Print our current length
        print(len(''.join(all_words)))
        print(all_words, even_words, odd_words)
        print(even_start, odd_start)
        # TODO: sort these by length of the next word (descending)
        print(next_words)
    else:
        # What do we do in this case?
        pass
    word = input("Enter the next word: ")
    word = word.upper()
    
