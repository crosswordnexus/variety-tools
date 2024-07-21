# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 19:58:38 2024

@author: boisv

Rows Garden Creation
"""
import os
import re
from collections import defaultdict

MIN_SCORE = 50

# Set up sets of words
WORDS = defaultdict(set)

# Read in the word list
with open(os.path.join('..', 'word_lists', 'spreadthewordlist.dict'), 'r') as fid:
    for line in fid:
        word, score = line.split(';')
        word = word.lower()
        score = int(score)
        if len(word) >= 6 and score >= MIN_SCORE:
            WORDS[len(word)].add(word)
#%%

def bloom_patterns(_input):
    """
    Return all twelve "rotations" of a word in a bloom
    """
    patterns = set()
    # reverse the string
    _input2 = _input[::-1]
    
    # Loop through all options
    for i in range(6):
        pat1 = _input[i:] + _input[:i]
        pat2 = _input2[i:] + _input2[:i]
        patterns.add(pat1)
        patterns.add(pat2)
    return patterns

def bloom_matches(_input):
    """
    Given a pattern, find possible bloom entries
    """
    # Set up our output variable
    output = set()
    
    # find words in words6 that match this
    for pat in bloom_patterns(_input):
        words1 = set(_ for _ in WORDS[6] if re.match(pat, _) is not None)
        output = output.union(words1)
    return output

def row_matches(_input):
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
    s = _input.lower()
    
    
    # bloombuds is an array of dictionaries
    # each dictionary has a three-letter pattern and a "start" integer
    bloombuds = []
    ctr = 0
    while s:
        s1, s = s[:3], s[3:]
        if re.match('[a-z\.]+', s1):
            d = {'bud': s1, 'start': ctr}
            bloombuds.append(d)
        ctr += 3
    #END while
    
    for w in WORDS[mylen]:
        for d in bloombuds:
            fullpat = d['bud'][::-1] + w[d['start']:d['start']+3]
        
    
    
    print(bloombuds)
            
    return 0
    


