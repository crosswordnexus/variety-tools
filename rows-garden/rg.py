# -*- coding: utf-8 -*-
"""
Rows Garden Creation

(c) 2024, Crossword Nexus and Joon Pahk.
MIT License -- https://opensource.org/license/MIT
"""
import os
from collections import defaultdict
import itertools
import re

MIN_SCORE = 50

# Set up sets of words
WORDS = defaultdict(set)

UPPERCASE_LETTERS = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

# Read in the word list
with open(os.path.join('..', 'word_lists', 'spreadthewordlist.dict'), 'r') as fid:
    for line in fid:
        word, score = line.split(';')
        word = word.lower()
        score = int(score)
        if len(word) >= 6 and score >= MIN_SCORE:
            WORDS[len(word)].add(word)
#%%
COLORS = ['light', 'medium', 'dark']
ROWS = 12
COLUMNS = 21
# function to determine the color, given the row and column
def cell_color(r, c):
    color1 = COLORS[((r-1)//2) % 3];
    color2 = COLORS[(1 + (r//2)) % 3]
    if r == 0 or r == ROWS - 1:
        color1 = 'empty'
    color = color2
    if c % 6 <= 2:
        color = color1
    return color

def bloom_patterns1(_input, backward=False):
    """
    Return the six rotations of a word in the given order
    """
    if backward:
        _input = _input[::-1]
    patterns = set()
    for i in range(6):
        pat = _input[i:] + _input[:i]
        patterns.add(pat)
    return patterns

def bloom_patterns(_input):
    """
    Return all twelve "rotations" of a word in a bloom
    """
    p1 = bloom_patterns1(_input)
    p2 = bloom_patterns1(_input, True)
    return p1.union(p2)

def bloom_matches(_input):
    """
    Given a pattern, find possible bloom entries
    """
    # Set up our output variable
    output = set()

    # find words in words6 that match this
    for pat in bloom_patterns(_input.lower()):
        words1 = set(_ for _ in WORDS[6] if simple_regex(pat)(_))
        output = output.union(words1)
    return output

def row_matches(_input, start_location=0):
    """
    Use _ for unconstrained letters,
    a-z or . for constrained letters based on the row above. Constrained letters
    must be in groups of 3. You may also use A-Z for fixed letters.

    For instance, if you put DELETED SCENE in at row B1,
    and you're looking for 12-letter entries at row C1,
    you would use del___dsc___ as input
    """

    # read the length of the input
    mylen = len(_input)

    # Set up blooms
    s = _input
    
    # if start_location != 0 we are looking at the second word in a row
    ix = (3 - start_location) % 3
    s = s[ix:]

    # bloombuds is an array of dictionaries
    # each dictionary has a three-letter pattern and a "start" integer
    bloombuds = []
    ctr = 0
    while s:
        s1, s = s[:3], s[3:]
        if is_lowercase_or_period(s1):
            d = {'bud': s1, 'start': ctr + ix}
            bloombuds.append(d)
        ctr += 3
    #END while
    
    # If _input has an uppercase letter we have to check if it matches
    if _input != _input.lower(): # i.e. not all lowercase
        pat = ''
        for let in _input:
            if let in UPPERCASE_LETTERS:
                pat += let.lower()
            else:
                pat += '.'
        myRe = simple_regex(pat)
    else:
        def myRe(x):
            return True
    
    good_words = dict()
    for w in WORDS[mylen]:
        if not myRe(w):
            continue
        if not bloombuds:
            if myRe(w):
                good_words[w] = []
        else:
            for d in bloombuds:
                fullpat = d['bud'][::-1] + w[d['start']:d['start']+3]
                # If there's no "." we can use bloom_patterns
                if '.' not in fullpat:
                    this_matches = bloom_patterns(fullpat).intersection(WORDS[6])
                else:
                    this_matches = bloom_matches(fullpat)
                if this_matches:
                    good_words[w] = good_words.get(w, []) + [this_matches.pop()]

    return dict([(x, k) for x, k in good_words.items() if len(k) == len(bloombuds)])
#END row_matches()

def simple_regex(pattern):
    """
    Return a function that matches simple patterns without the overhead of regex
    """
    pattern = pattern.lower()
    def matcher(word):
        if len(word) != len(pattern):
            return False
        word = word.lower()
        for p, w in zip(pattern, word):
            if p != '.' and p != w:
                return False
        return True
    return matcher

def is_lowercase_or_period(s):
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz.")
    return all(char in allowed_chars for char in s)

def fill_row(row_above, row_number):
    # Set up the return object
    output = dict()
    
    # Further modify "row_above" based on the row_number
    row_above2 = ''
    for i, let in enumerate(row_above):
        if cell_color(row_number, i) == cell_color(row_number - 1, i):
            row_above2 += let
        elif let in UPPERCASE_LETTERS:
            row_above2 += let
        else:
            row_above2 += '_'
    row_above = row_above2
    
    minLen, maxLen = 6, 15
    # We need to change some stuff if we're in the last row
    if row_number == ROWS - 1:
        minLen, maxLen = 9, 9
        row_above = row_above.replace('_', '')
    
    for mylen in range(minLen, maxLen+1): # from 6-15
        
        # Step 1: find options for the first entry
        pat1 = row_above[:mylen]
        rm1 = row_matches(pat1)
        
        # Step 2: find options for the second entry
        rm2 = row_matches(row_above[mylen:], mylen)
        
        # At the last row, we can just return rm1
        if row_number == ROWS - 1:
            for k, v in rm1.items():
                output[(k, '')] = v
            return output
        
        # Make sure we have matches
        if not rm1 or not rm2:
            continue
        
        # Step 3: make sure these line up
        # Iterate through rm1 and rm2
        for k1 in rm1.keys():
            for k2 in rm2.keys():
                # We need to make sure that the end of k1 
                # and the start of k2 will make a valid bloom
                start_col = mylen
                num_end_letters = mylen % 3
                # We only need to do this if it's not a multiple of 3
                if num_end_letters > 0:
                    k1_end_reversed = k1[-num_end_letters:][::-1]
                    k2_start = k2[:(3-num_end_letters)]
                    if cell_color(row_number - 1, start_col) == cell_color(row_number, start_col):
                        pat = k2_start + k1_end_reversed + row_above[mylen - num_end_letters:mylen - num_end_letters + 3]
                        pat = pat.replace('_', '.')
                    else:
                        pat = k2_start + k1_end_reversed + '...'
                    if not bloom_patterns(pat):
                        continue
                k = (k1, k2)
                v = rm1[k1] + rm2[k2]
                # Make a final check if this is the penultimate row
                if row_number == ROWS - 2:
                    this_row = k1 + k2
                    this_match = this_row[3:6] + this_row[9:12] + this_row[15:18]
                    if not row_matches(this_match):
                        continue
                output[k] = v
    return output
#%% Run some rows
# Note: if row_number == 1 you have to modify `row_above`
# to look like ___jum___psc___are___
row_above = 'undercoveragentpelosi'
row_number = 2
output = fill_row(row_above, row_number)

print(output)

#%% Function to return all "good" nine-letter matches for the penultimate row
# This could be useful for testing the last row
# however this takes FOREVER to run

def find_nine_matches():
    output = set()
    # Loop through nine-letter words
    for w in WORDS[9]:
        # Find bloom matches for the first, second, and third trigrams
        w1, w2, w3 = [w[i:i+3] for i in range(0, len(w), 3)]
        b1 = bloom_matches(f"{w1}...")
        b2 = bloom_matches(f"{w2}...")
        b3 = bloom_matches(f"{w3}...")
        for s1, s2, s3 in itertools.product(b1, b2, b3):
            t1 = extract_remaining_letters(s1, w1)[::-1]
            t2 = extract_remaining_letters(s2, w2)[::-1]
            t3 = extract_remaining_letters(s3, w3)[::-1]
            output.add(t1 + t2 + t3)
    return output


def extract_remaining_letters(long_string, short_string):
    """
    look for the remaining letters in a string, once short_string is removed
    """
    for b in bloom_patterns(long_string):
        if b.startswith(short_string):
            return b[len(short_string):]
    return None

