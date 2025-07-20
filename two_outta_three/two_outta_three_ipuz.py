# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 21:12:26 2022

@author: Alex Boisvert

Convert an iPuz from CrossFire/Ingrid into a "two outta three ain't bad" iPuz file
"""

import json
import re
from collections import defaultdict

filename = r'TwoOuttaThree.ipuz'

with open(filename, encoding='utf-8') as fid:
    puz = json.load(fid)
    
#%% How many of each clue type do we have?
# For this we assume each clue is like [ANGERED / ANGERED (as)]
clues = puz['clues']

clue_types = defaultdict(int)
for _, cluelist in clues.items():
    for clue_arr in cluelist:
        num, clue = clue_arr
        r = re.search(r'\((.*)\)', clue)
        if r is not None:
            m = r.groups()[0]
            k = json.dumps(sorted(m))
            clue_types[k] += 1
            
print(clue_types)
    
#%% Do some bookeeping
puz['fakeclues'] = True
# First, sort the components of the clues (just to be safe)
# and make them uppercase
# and remove the numbers
# then sort the clue list

for key, cluelist in clues.items():
    new_clue_arr = []
    for clue_arr in cluelist:
        num, clue = clue_arr
        clue = clue.upper()
        # take out any notes we may have added
        if '(' in clue:
            clue = clue.split('(')[0].strip()
        w1, w2 = re.split(r'\s+\/\s+', clue)
        new_clue = ' / '.join(sorted([w1, w2]))
        new_clue_arr.append(['', new_clue])
    new_clue_arr = sorted(new_clue_arr, key=lambda x: x[1])
    clues[key] = new_clue_arr
    
# Make an intro (and notes)
puz['intro'] = '''Each answer in this puzzle is a lowercase dictionary word. Clues come in three types: anagrams, rhymes, and synonyms of the answer word. However, for each answer, only two of the three types of clues are given. It is up to you to determine which clue is which type. Clues are given in alphabetical order.'''
puz['notes'] = puz['intro']

#%% Preview
j = json.dumps(puz, indent=2)

#%% Write the file
with open(filename, 'w') as fid:
    json.dump(puz, fid, indent=2)
