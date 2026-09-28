#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 09:19:00 2025

@author: alexboisvert
"""
from acrostic_glp import alpha_only, create_acrostic2, are_there_dupes, get_seed_words
from pathlib import Path
from collections import Counter

source = """Veronica Mars"""

quote = '''
Tragedy blows through your life like a tornado. 
You wait for the dust to settle, and then you choose. 
You can live in the wreckage and pretend it's still the mansion 
you remember. Or you can crawl from the rubble and slowly rebuild.
'''.strip().replace('\n', ' ').replace('  ', ' ')

print(f"Quote length: {len(alpha_only(quote))}")
print(f"Source length: {len(alpha_only(source))}")

print(f"Average entry length: {len(alpha_only(quote))/len(alpha_only(source)):2f}")

# Check that the source is contained in the quote
missing_letters = Counter(alpha_only(source)) - Counter(alpha_only(quote))
if missing_letters:
    print("Source is not contained in quote")
    print(missing_letters)

#%% Look for seed words
seed_words = get_seed_words(quote, source)

#%%
excluded = ['newyorkherald', 'ELENARYBAKINA', 'JOEYBUTTAFUOCO', 'littleboyblue', 
            'offoffbroadway', 'lutherburbank', 'sarahrafferty', 'LINDAELLERBEE', 'OUTOFLEFTFIELD'
            , 'ALUTACONTINUA', 'shakeoneshead', 'motherhubbard', 'onlittlecatfeet',
            'leotardballet', 'MOUNTLYCABETTUS', 'rightunderyournose']
included = ['complimentsandwich', 
            'rubbedthewrongway',
            'nostringsattached',
            'videodailydouble']
wordlist, minscore = Path('../word_lists/spreadthewordlist.dict'), 50
wordlist, minscore = Path('../word_lists/nediger_list.txt'), 50

# Check the new ratio
q2 = len(alpha_only(quote)) - len(''.join(included))
s2 = len(alpha_only(source)) - len(included)
print(f"=====\nAverage entry length: {(q2/s2):2f}\n=====\n")


soln_array = create_acrostic2(
    quote, source,
    excluded_words=excluded,
    included_words=included,
    wordlist=wordlist,
    min_score=minscore,
    len_distance=3
)

print(soln_array)

for x in soln_array:
    print(x.upper())

#%%
are_there_dupes(soln_array)

