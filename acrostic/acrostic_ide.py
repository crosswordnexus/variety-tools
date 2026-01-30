#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 09:19:00 2025

@author: alexboisvert
"""
from acrostic_glp import alpha_only, create_acrostic2, are_there_dupes, get_seed_words
from pathlib import Path

source = '''megan amram'''

quote = '''
when singers at concerts hold out the mic for the audience to sing
it's like what am i, your maid
'''.strip().replace('\n', ' ').replace('  ', ' ')

print(f"Quote length: {len(alpha_only(quote))}")
print(f"Source length: {len(alpha_only(source))}")

print(f"Average entry length: {len(alpha_only(quote))/len(alpha_only(source)):2f}")

#%% Look for seed words
seed_words = get_seed_words(quote, source)

#%%
excluded = ['newyorkherald']
included = []
wordlist = Path('../word_lists/spreadthewordlist.dict')
minscore = 50

soln_array = create_acrostic2(
    quote, source,
    excluded_words=excluded,
    included_words=included,
    wordlist=wordlist,
    min_score=minscore,
    len_distance=2
)

for x in soln_array:
    print(x.upper())
    
#%%
are_there_dupes(soln_array)
